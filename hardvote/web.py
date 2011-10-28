import json
import logging
import lxml.html

from lxml import etree
from lxml.etree import Element, SubElement

from hardvote import NS

class Handlers:
	@classmethod
	def get(cls, node, qn):
		func = getattr(cls, node.attrib.get('type'), None)
		if func is None:
			print(node.attrib.get('type'), 'has no matching handler!')
			return

		div = Element("div", {
			"class": "question " + node.attrib.get('type'),
			"id": "question" + str(qn)
		})
		label = etree.XML("<h2>%s) %s</h2>" % (qn, node.find(NS['poll'] + "text").text))
		div.append(label)

		div = func(node, qn, div)
		
		if node.attrib.get('mode') == "required":
			label.append(etree.XML("<span class='asterisk'>*</span>"))
			for input in div.getiterator("input"):
				input.attrib['required'] = 'required'
			for input in div.getiterator("textarea"):
				input.attrib['required'] = 'required'

		return div
	
	@classmethod
	def multiple(cls, node, qn, div):
		ol = SubElement(div, "ol")
		for n, option in enumerate(node.find(NS['poll'] + "options").getchildren()):
			li = SubElement(ol, "li")
			inp = SubElement(li, "input", {
				"id": "question%s-%s" % (qn, str(n)),
				"type": "radio",
				"name": "response" + str(qn),
				"value": str(n+1)
			})
			SubElement(li, "label", {"for":"question%s-%s" % (qn, n)}).text = option.text
		return div

	@classmethod
	def shorttext(cls, node, qn, div):
		SubElement(div, "input", {
			"id": "question" + str(qn),
			"type": "text",
			"name": "response" + str(qn)
		})
		return div

	@classmethod
	def longtext(cls, node, qn, div):
		SubElement(div, "textarea", {
			"id": "question" + str(qn),
			"name": "response" + str(qn),
			"placeholder": "Enter response here..."
		})
		return div

	@classmethod
	def gauge(cls, node, qn, div):
		ol = SubElement(div, "ol")
		for n in range(int(node.attrib.get('min', 0)), int(node.attrib.get('max', 10))+1):
			li = SubElement(ol, "li")
			inp = SubElement(li, "input", {
				"id": "question%s-%s" % (qn, str(n)),
				"type": "radio",
				"name": "response" + str(qn),
				"value": str(n)
			})
			SubElement(li, "label", {"for":"question%s-%s" % (qn, n)}).text = str(n)
		
		'''
		SubElement(div, "input", {
			"id": "question" + str(qn),
			"type": "range",
			"max": node.attrib.get("max", 10),
			"min": node.attrib.get("min", 0)
		})
		'''
		return div

	@classmethod
	def preferential(cls, node, qn, div):
		length = len(node.find(NS['poll'] + "options").getchildren())
		for n, option in enumerate(node.find(NS['poll'] + "options").getchildren()):
			p = SubElement(div, "p")
			inp = SubElement(p, "input", {
				"type": "number",
				"name": "response%s-%s" % (qn, str(n)),
				"id": "response%s-%s" % (qn, str(n)),
				"min": "1",
				"max": str(length)
			})
			SubElement(p, "label", {"for":"response%s-%s" % (qn, n)}).text = option.text
		return div

class HTMLGenerator(object):
	def __str__(self):
		return "<!DOCTYPE html>\n" + etree.tostring(self.html, pretty_print=True, method="html").decode()

	def get_page(self):
		return str(self)

	def __init__(self, border_page, node):
		self.html = etree.parse(border_page, etree.HTMLParser()).getroot()
		self.form = self.get_form(node)
		self.html.xpath('/html/body/div[contains(@id, "poll")]')[0].append(self.form)
		
		title = node.xpath('/poll/settings/title')
		if len(title) > 0:
			title = title[0].text
		else:
			title = "Poll"

		self.html.xpath('/html/head/title')[0].text = title
		
		#el = self.html.xpath('/html/body/form[contains(@id, "poll")]')[0]
		#self.html.replace(el, self.form)

	def get_form(self, node):
		ns = NS['poll']
		form = Element("form", method="post", id="poll-form")
		qn = 0
		for n, element in enumerate(node.getiterator(ns + "section")):
			section = SubElement(form, "div", {
				"class": "section",
				"id": str(n + 1)
			})

			if element.attrib.get("title"):
				SubElement(section, 'h1').text = element.attrib["title"]

			for question in element.getchildren():
				qn += 1
				try:
					if question.tag != ns + "question":
						continue
					#func = getattr(self, "get_%s" % question.attrib.get('type'))
					#div = func(question, qn)
					div = Handlers.get(question, qn)
					#div = self.set_validation(question, div)	
					
					section.append(div)
				
				except AttributeError as e:
					print(e) # XXX stub
					print(question.attrib)
		
		form.append(self.get_submit_section())
		return form


	def get_submit_section(self):	
		section = Element("div", {
			"class": "section",
			"id": "submit"
		})
		SubElement(section, 'p').text = "Once you press submit, your response is final unless there are errors, in which case you will allowed to correct them."
		SubElement(section, 'input', id="poll-submit", type='submit', value="Submit")
		return section


