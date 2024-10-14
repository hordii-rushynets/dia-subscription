""" Обгортка над бібліотекою підпису користувача ЦСК """

# -*- coding: utf-8 -*-
from EUSignCP import *
import json
import base64
import datetime

class EUSign():
	""" 
		Класс обгортка над бібліотекою підпису користувача ЦСК

	"""

	SIGN_TYPE_UNKNOWN = EU_SIGN_TYPE_UNKNOWN
	SIGN_TYPE_CADES_BES = EU_SIGN_TYPE_CADES_BES
	SIGN_TYPE_CADES_T = EU_SIGN_TYPE_CADES_T
	SIGN_TYPE_CADES_C = EU_SIGN_TYPE_CADES_C
	SIGN_TYPE_CADES_X_LONG = EU_SIGN_TYPE_CADES_X_LONG
	SIGN_TYPE_CADES_X_LONG_TRUSTED = EU_SIGN_TYPE_CADES_X_LONG_TRUSTED

	def __init__(self):
		self.lib = None
		self.cas = None
		self.context = None

	def __del__(self):
		self.__finalize()
	
	def __finalize(self):
		if self.lib != None:
			if self.context != None:
				self.lib.CtxFree(self.context)
				self.context = None
			self.lib.Finalize()
			self.lib = None
		EUUnload()

	def __map_date(self, date):
		return datetime.datetime(
			date['wYear'], date['wMonth'], date['wDay'], 
			date['wHour'], date['wMinute'], date['wSecond'])

	def __set_settings(self, cas_file_name, ca_certs_file_name):
		""" Налаштування бібліотеки з встановленням: 
			файлового сховища сертифікатів, proxy-сервера, OCSP-, TSP-, LDAP- та CMP-серверів ЦСК
			із використання файлів параметрів ЦСК (CAs.json) та списку сертифікатів (CACertificates.p7b)

		"""

		# Вимкнення збереження налаштувань до реєстру або файлу початкових параметрів (osplm.ini)
		self.lib.SetRuntimeParameter(
			EU_SAVE_SETTINGS_PARAMETER, EU_SETTINGS_ID_NONE)

		# Встановлення типу контейнера CAdES для підпису, що накладається криптобібліотекою
		# За замовчанням - CAdES-BES (EU_SIGN_TYPE_CADES_BES)
		self.lib.SetRuntimeParameter(EU_SIGN_TYPE_PARAMETER, EU_SIGN_TYPE_CADES_BES)

		# Встановлення налаштувань сховища сертифікатів та СВС
		fs = {
			'szPath': '', # встановлено для використання віртуального сховища сертифікатів та СВС в пам'яті
			'bCheckCRLs': False,
			'bAutoRefresh': False,
			'bOwnCRLsOnly': False,
			'bFullAndDeltaCRLs': False,
			'bAutoDownloadCRLs': False,
			'bSaveLoadedCerts': False,
			'dwExpireTime': 3600
		}
		self.lib.SetFileStoreSettings(fs)

		# Встановлення параметрів proxy-сервера для доступу к серверам ЦСК
		proxy = {
			'bUseProxy': False,
			'bAnonymous': False,
			'szAddress': "",
			'szPort': "",
			'szUser': "",
			'szPassword': "",
			'bSavePassword': False
		}
		self.lib.SetProxySettings(proxy)

		# Встановлення параметрів OCSP-сервера ЦСК за замовчанням
		ocsp = {
			'bUseOCSP': True,
			'bBeforeStore': True,
			'szAddress': "czo.gov.ua",
			'szPort': "80"
		}
		self.lib.SetOCSPSettings(ocsp)

		# Встановлення параметрів TSP-сервера ЦСК за замовчанням
		tsp = {
			'bGetStamps': True,
			'szAddress': "czo.gov.ua",
			'szPort': "80"
		}
		self.lib.SetTSPSettings(tsp)

		# Встановлення параметрів LDAP-сервера ЦСК
		ldap = {
			'bUseLDAP': False,
			'szAddress': "",
			'szPort': "",
			'bAnonymous': False,
			'szUser': "",
			'szPassword': ""
		}
		self.lib.SetLDAPSettings(ldap)

		# Встановлення параметрів CMP-сервера ЦСК
		cmp = {
			'bUseCMP': False,
			'szAddress': "",
			'szPort': "",
			'szCommonName': ""
		}
		self.lib.SetCMPSettings(cmp)

		# Встановлення параметрів взаємодії з TSP-, OCSP- і CMP-серверами ЦСК
		# Використання режиму он-лайн
		offline_mode = {
			'bOfflineMode': False
		}
		self.lib.SetModeSettings(offline_mode)

		# Встановлення налаштувань точок доступу до OCSP-серверів з файлу параметрів ЦСК (CAs.json)
		# Необхідні при обслуговуванні користувачів з різних ЦСК
		with open(cas_file_name, "r", encoding='utf-8') as cas_file:
			cas = json.load(cas_file)
		self.cas = cas

		ocsp_access_info_mode = {
			'bEnabled': True
		}
		self.lib.SetOCSPAccessInfoModeSettings(ocsp_access_info_mode)

		for ca in cas:
			for issuer_cn in ca['issuerCNs']:
				ocsp_access_info = {
					'szIssuerCN': issuer_cn,
					'szAddress': ca['ocspAccessPointAddress'], 
					'szPort': ca['ocspAccessPointPort']
				}
				self.lib.SetOCSPAccessInfoSettings(ocsp_access_info)	

		# Збереження кореневих сертифікатів ЦЗО та ЦСК (НЕДП)
		with open(ca_certs_file_name, "rb") as ca_certs_file:
			ca_certs = ca_certs_file.read()
			self.lib.SaveCertificates(ca_certs, len(ca_certs))

		context = []
		self.lib.CtxCreate(context)
		self.context = context[0]

	def initialize(self, cas_file_name, ca_certs_file_name):
		"""	Ініціалізація бібліотеки та встановлення налаштувань 
			з використаннм файлів CAs.json (cas_file_name) та 
			CACertificates.p7b (ca_certs_file_name).

			Актуальні параметрів ЦСК (CAs.json) та списку сертифікатів (CACertificates.p7b) можуть бути завантажені за посиланнями: 
			https://iit.com.ua/download/productfiles/CAs.json
			https://iit.com.ua/download/productfiles/CACertificates.p7b

		"""

		if self.lib != None:
			return

		try:
			EULoad()
			self.lib = EUGetInterface()

			self.lib.SetUIMode(False)
			self.lib.Initialize()
			self.lib.SetUIMode(False)

			self.__set_settings(cas_file_name, ca_certs_file_name)
		except Exception as e:
			self.__finalize()
			raise e

	def __date_to_string(self, time):
		return self.__map_date(time).strftime("%d.%m.%y %H:%M:%S")

	def hash_data(self, data):
		""" Метод повертає геш (ГОСТ 34.311) у вигляді base64 строки отриманий з даних (data) """

		hash = []
		self.lib.CtxHashData(self.context,
			EU_CTX_HASH_ALGO_GOST34311, None, 0, data, len(data), hash)

		return base64.b64encode(hash[0])

	def print_verify_results(self, data_file_path, sign_file_path, results):
		""" Метод відображення результату перевірки підписів, що були отриманні з використанням функцій cades_verify_data та cades_verify_data_internal"""
		print ("Verify signature result:")
		print ("\tData file path- " + data_file_path)
		print ("\tSign file path- " + sign_file_path)

		sign_types = {
			EU_SIGN_TYPE_CADES_BES: "CAdES-BES",
			EU_SIGN_TYPE_CADES_T: "CAdES-T",
			EU_SIGN_TYPE_CADES_C: "CAdES-T",
			EU_SIGN_TYPE_CADES_X_LONG: "CAdES-X-Long",
			(EU_SIGN_TYPE_CADES_X_LONG + EU_SIGN_TYPE_CADES_X_LONG_TRUSTED): "CAdES-X-Long-Trusted"
		}

		for i in range(len(results)):
			print ("Sign container type: " + results[i]["cadesType"])
			print ("Sign type: " + sign_types[results[i]["signType"]])
			print ("Signer info:")
			print ("Signer CN: " + results[i]["infoEx"]["pszSubjCN"])
			print ("Certificate issuer CN: " + results[i]["infoEx"]["pszIssuerCN"])
			print ("Certificate serial: " + results[i]["infoEx"]["pszSerial"])

			if results[i]["timeInfo"]["bTimeAvail"] :
				print (("Data time stamp" if results[i]["timeInfo"]["bTimeStamp"] else "Signing time") + ": " + self.__date_to_string(results[i]["timeInfo"]["Time"]))

			if results[i]["timeInfo"]["bSignTimeStampAvail"] :
				print ("Sign time stamp: " + self.__date_to_string(results[i]["timeInfo"]["SignTimeStamp"]))

		print ("")

	def cades_make_container(self, signature, data, sign_type):
		"""	Формування нового CAdES контейнеру на основі існуючого за вхідними параметрами 
			Якщо data == None формується зовнішній підпис (CAdES-detached), в іншому випадку формується внутрішній підпис (CAdES-enveloped)
		"""
		try:
			# Отримання кількості підписувачів для існуючого підпису
			signs_count = []
			self.lib.GetSignsCount(signature, None, 0, signs_count)
			signs_count = signs_count[0]

			# Створення нового контейнеру з підписом
			new_signature = [];
			self.lib.CreateEmptySign(data, len(data) if data != None else 0, new_signature, None)
			new_signature = new_signature[0]

			for i in range(signs_count):
				info = {}
				certificate = []
				signer = []
				cur_sign_type = []
				result = []

				# Отримання інформації та сертифікату підписувача
				self.lib.GetSignerInfo(i, signature, None, 0, info, certificate)
				certificate = certificate[0]

				# Отримання підписувача з підпису
				self.lib.GetSigner(i, signature, None, 0, signer, None)
				signer = signer[0]

				# Отримання інформації про поточний тип підпису
				self.lib.GetSignType(i, signature, None, 0, cur_sign_type)
				cur_sign_type = cur_sign_type[0]

				# Додавання додаткових даних для перевірки підпису лише у випадку якщо їх не має
				if sign_type > cur_sign_type:
					newSigner = []
					self.lib.AppendValidationDataToSignerEx(signer, None, 0, certificate, len(certificate), sign_type, newSigner, None)
					signer = newSigner[0]

				# Додавання підписувача до контейнеру з новим підписом
				self.lib.AppendSigner(signer, None, 0, certificate, len(certificate), new_signature, None, 0, result, None)
				new_signature = result[0]

			return new_signature
		except Exception as e:
			d_error = eval(str(e))
			raise Exception("An error occurred while making CAdES container. Error code: " + str(d_error['ErrorCode']) + ". Description: " + d_error['ErrorDesc'].decode())

	def cades_verify_data(self, data, signature):
		""" Метод перевірки зовнішнього підпису (CAdES-detached)"""
		try:
			# Отримання кількості підписувачів
			signs_count = []
			self.lib.GetSignsCount(signature, None, 0, signs_count)
			signs_count = signs_count[0]

			signs_infos = []

			# Перевірка підписів
			for i in range(signs_count):
				sign_info = {}
				certificate = []

				# Перевірка підпису
				self.lib.VerifyDataSpecific(data, len(data), i, signature, None, 0, sign_info)
				sign_info = {}

				sign_info["cadesType"] = "detached"
				# Отримання інформації про тип підпису
				sign_type = []
				self.lib.GetSignType(i, signature, None, 0, sign_type)
				sign_info["signType"] = sign_type[0]
				# Отримання інформації про сертифікат підписанта
				info = {}
				self.lib.GetSignerInfo(i, signature, None, 0, info, certificate)
				sign_info["infoEx"] = info
				# Отримання інформації про час підпису
				time_info = {}
				self.lib.GetSignTimeInfo(i, signature, None, 0, time_info)
				sign_info["timeInfo"] = time_info
				signs_infos.append(sign_info)

			return signs_infos
		except Exception as e:
			d_error = eval(str(e))
			raise Exception("An error occurred while verify CAdES-detached. Error code: " + str(d_error['ErrorCode']) + ". Description: " + str(d_error['ErrorDesc']).decode())

	def cades_verify_data_internal(self, signature):
		""" Метод перевірки внутрішнього підпису (CAdES-enveloped)"""
		try:
			# Отримання кількості підписувачів
			signs_count = []
			self.lib.GetSignsCount(signature, None, 0, signs_count)
			signs_count = signs_count[0]

			signs_infos = []

			# Перевірка підписів
			for i in range(signs_count):
				sign_info = {}
				certificate = []
				data = []

				# Перевірка підпису
				self.lib.VerifyDataInternalSpecific(i, signature, None, 0, data, sign_info)
				data = data[0]
				sign_info = {}

				sign_info["cadesType"] = "enveloped"
				# Отримання інформації про тип підпису
				sign_type = []
				self.lib.GetSignType(i, signature, None, 0, sign_type)
				sign_info["signType"] = sign_type[0]
				# Отримання інформації про сертифікат підписанта
				info = {}
				self.lib.GetSignerInfo(i, signature, None, 0, info, certificate)
				sign_info["infoEx"] = info
				# Отримання інформації про час підпису
				time_info = {}
				self.lib.GetSignTimeInfo(i, signature, None, 0, time_info)
				sign_info["timeInfo"] = time_info
				signs_infos.append(sign_info)

			return data, signs_infos
		except Exception as e:
			d_error = eval(str(e))
			raise Exception("An error occurred while verify CAdES-enveloped. Error code: " + str(d_error['ErrorCode']) + ". Description: " + str(d_error['ErrorDesc']).decode())