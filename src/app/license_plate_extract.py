from config import KODE_WILAYAH_JSON
from config import REPLACE_ABJAD2NUMBER_DICT, REPLACE_NUMBER2ABJAD_DICT

from similarity.weighted_levenshtein import WeightedLevenshtein
from similarity.weighted_levenshtein import CharacterSubstitutionInterface

'''
Add cost substituting word in compnames and result ocr
'''
class AreaCodeCharacterSubstitution(CharacterSubstitutionInterface):
	def cost(self, char_true, char_false):
		# print(c0)
		if char_true == 'B' and char_false == '8': return 0.5
		if char_true == 'A' and char_false == '7': return 0.5
		if char_true == 'D' and char_false == '0': return 0.5
		return 1.0

class LicensePlateExtract:
	def __init__(self, results_ocr):
		self.weighted_levenshtein_area_code = WeightedLevenshtein(AreaCodeCharacterSubstitution())
		self.filtered_text = self.__filter_text_conf(results_ocr)

		self.text_list = [text for text,_ in self.filtered_text]
		self.conf_list = [conf for _,conf in self.filtered_text]
		self.license_plate_dict = dict()
		self.get_area_code(), self.get_license_number(), self.get_unique_area()

	def __filter_text_conf(self, results_ocr):
		'''
		Remove space in list text_conf and add create new list
		Args:
			text_conf(list): text condidence result ocr -> [['8 1549 RFS', 0.7276318370729566]]
		Return:
			new_text_conf(list): new text confidence -> [['8', 0.7276318370729566], ['1549', 0.7276318370729566], ['RFS', 0.7276318370729566]]
		'''
		new_text_conf = list()

		text_conf  = [[i[1], i[2]] for i in results_ocr]
		for text, conf in text_conf:
			remove_space = text.split(' ')
			for word in remove_space:
				if word.isalnum():
					new_text_conf.append([word, conf])

		new_text_conf_2 = list()
		if len(new_text_conf) <= 2:
			for text, conf in new_text_conf:
				if not text[0].isnumeric() and text[1:].isnumeric() and len(text)>4: # Pattren B3356 K0
					new_text_conf_2.append([text[0], conf])
					new_text_conf_2.append([text[1:], conf])
				elif text[:4].isnumeric() and text[4:].isalpha():
					new_text_conf_2.append([text[:4], conf])
					new_text_conf_2.append([text[4:], conf])
				else: new_text_conf_2.append([text, conf])

			return new_text_conf_2
		return new_text_conf

	def __replace_abjad2number(self, text, conf):
		'''
		Replace abjad to number in word result ocr
		Args:
			text(str): text to replace
			conf(float): confidence level text
		Return:
			new_text(str): new text after replaced
			ne_conf(float): new confidence after replace
		'''
		new_text = text
		new_conf = conf
		for i in range(len(new_text)):
			if not new_text[i].isnumeric() and new_text[i] in REPLACE_ABJAD2NUMBER_DICT:
				replaced = REPLACE_ABJAD2NUMBER_DICT[str(new_text[i])]
				new_text = new_text.replace(new_text[i], replaced)
				new_conf = (conf+1)/2
		return new_text, new_conf

	def __replace_number2abjad(self, text, conf):
		'''
		Replace number to abjad in word result ocr
		Args:
			text(str): text to replace
			conf(float): confidence level text
		Return:
			new_text(str): new text after replaced
			ne_conf(float): new confidence after replace
		'''
		new_text = text
		new_conf = conf
		for i in range(len(new_text)):
			if new_text[i].isnumeric() and new_text[i] in REPLACE_ABJAD2NUMBER_DICT:
				replaced = REPLACE_NUMBER2ABJAD_DICT[str(new_text[i])]
				new_text = new_text.replace(new_text[i], replaced)
				new_conf = (conf+1)/2
		return new_text, new_conf

	def get_area_code(self):
		'''
		Get area code license plate indonesia
		'''
		index = [i for i,x in enumerate(self.text_list) if len(x) <= 2 and not x.isnumeric()]
		if index:
			for idx in index:
				if self.text_list[idx] in KODE_WILAYAH_JSON:
					self.license_plate_dict.update({'area_code': [self.text_list[idx], self.conf_list[idx]]})
					break
				else : self.get_area_code_more()
		else : self.get_area_code_more()

	def get_area_code_more(self):
		'''
		filtered text with minimum pattren area code
		Get Area Code with algoritm weighted_levenshtein
		and update confidence (conf+1)/2
		'''
		min_ratio   = 10
		temp        = str()
		conf_i      = float()
		for text, conf in self.filtered_text:
			if len(text) in range(1, 4):
				text = text[1:] if text[0] in ['I', '1'] else text
				for area in KODE_WILAYAH_JSON:
					ratio = self.weighted_levenshtein_area_code.distance(area, text)
					if ratio < min_ratio:
						min_ratio = ratio
						temp = area
						conf_i = (conf+1)/2
					else:
						min_ratio = min_ratio
						temp = temp
						conf_i = conf_i
		if min_ratio < 1.5 and temp in KODE_WILAYAH_JSON:
			self.license_plate_dict.update({'area_code': [temp, conf_i]})
		else:
			self.license_plate_dict.update({'area_code': ['', 0]})

	def get_license_number(self):
		'''
		Get license plate number
		'''
		index = [i for i,x in enumerate(self.text_list) if len(x) == 4 and x.isnumeric() and not x[0] in ['0', 'O']]
		if index:
			for idx in index:
				self.license_plate_dict.update({'license_number': [self.text_list[idx], self.conf_list[idx]]})
				break
		else: self.get_license_number_more()
	
	def get_license_number_more(self):
		'''
		filtered text with minimum pattren license numeber
		Get license numeber with process replace number/abjad
		and update confidence (conf+1)/2
		'''
		for text, conf in self.filtered_text:
			if len(text) in range(2, 5) and not text.isalpha() and not text[0] in ['0', 'O']:
				if text.isnumeric():
					self.license_plate_dict.update({'license_number': [text, conf]})
					break
				else:
					text, conf = self.__replace_abjad2number(text, conf)
					self.license_plate_dict.update({'license_number': [text, conf]})
					break
		try:
			self.license_plate_dict.update['license_number']
		except:
			for idx, (text, conf) in enumerate(self.filtered_text):
				if text.isalnum() and not text.isnumeric() and len(text) > 4 and text[0].isnumeric(): # Pattren B 3356K0
					search_num = [char for char in text if char.isdigit()]
					if len(search_num) <= 4:
						self.license_plate_dict.update({'license_number': [text[:len(search_num)], conf]})
						self.filtered_text[idx] = [text[len(search_num):], conf]
					else:
						self.license_plate_dict.update({'license_number': [text[:4], conf]})
						self.filtered_text[idx] = [text[4:], conf]
					break
	
	def get_unique_area(self):
		'''
		Get unique area in license plate
		'''
		index = [i for i,x in enumerate(self.text_list) if len(x) == 3 and x.isalpha()]
		if index:
			for idx in index:
				self.license_plate_dict.update({'unique_are': [self.text_list[idx], self.conf_list[idx]]})
				break
		else: self.get_unique_area_more()

	def get_unique_area_more(self):
		'''
		filtered text with minimum pattren unique area plate
		Get unique area plate with process replace number/abjad
		and update confidence (conf+1)/2
		'''
		for text, conf in self.filtered_text:
			if len(text) in range(2, 5) and not text.isnumeric() and text not in self.license_plate_dict['area_code'][0]:
				if text.isalpha():
					text = text[:3] if len(text) >3 else text
					self.license_plate_dict.update({'unique_are': [text, conf]})
					break
				else:
					text, conf = self.__replace_number2abjad(text, conf)
					text = text[:3] if len(text) >3 else text
					self.license_plate_dict.update({'unique_are': [text, conf]})
					break
		
		try: self.license_plate_dict['unique_are']
		except: self.license_plate_dict.update({'unique_are': ['', 0]})