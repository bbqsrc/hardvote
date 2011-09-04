import json
import logging
import lxml.html

from lxml import etree
from lxml.etree import Element, SubElement

XMLNS = {
	'poll': "http://bbqsrc.net/xml/poll/0.1"
}

NS = {}
for k, v in XMLNS.items():
	NS[k] = "{%s}" % v


class HTMLGenerator(object):
	def __str__(self):
		return lxml.html.tostring(self.form, pretty_print=True).decode()

	def __init__(self, border_page, xmlf, output_path):
		ns = NS['poll']

		form = Element("form", id="poll")
		root = etree.parse(xmlf)

		qn = 0
		for n, element in enumerate(root.getiterator(ns + "section")):
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
					func = getattr(self, "get_%s" % question.attrib.get('type')
					section.append(func(question, qn))
				except AttributeError as e:
					print(e) # XXX stub
					print(question.attrib)
		self.form = form

	def get_multiple(self, x, qn):
		div = Element("div", {
			"class": "question multiple",
			"id": "question" + str(qn)
		})
		div.append(etree.XML("<h2>%s) %s</h2>" % (qn, x.find(NS['poll'] + "text").text)))

		ol = SubElement(div, "ol")
		for n, option in enumerate(x.find(NS['poll'] + "options").getchildren()):
			li = SubElement(ol, "li")
			inp = SubElement(li, "input", {
				"type": "radio",
				"name": "response" + str(qn),
				"value": str(n+1)
			})
			SubElement(li, "span").text = option.text
		return div

	def get_shorttext(self, x, qn):
		div = Element("div", {
			"class": "question shorttext",
			"id": "question" + str(qn)
		})
		div.append(etree.XML("<h2>%s) %s</h2>" % (qn, x.find(NS['poll'] + "text").text)))

		SubElement(div, "input", {
			"type": "text",
			"name": "response" + str(qn)
		})
		return div

	def get_longtext(self, x, qn):
		div = Element("div", {
			"class": "question longtext",
			"id": "question" + str(qn)
		})
		div.append(etree.XML("<h2>%s) %s</h2>" % (qn, x.find(NS['poll'] + "text").text)))

		SubElement(div, "textarea", {
			"name": "response" + str(qn),
			"placeholder": "Enter response here..."
		})
		return div

	def get_gauge(self, x, qn):
		div = Element("div", {
			"class": "question gauge",
			"id": "question" + str(qn)
		})
		div.append(etree.XML("<h2>%s) %s</h2>" % (qn, x.find(NS['poll'] + "text").text)))

		ul = SubElement(div, "ul")
		for n in range(int(x.attrib.get('min', 0)), int(x.attrib.get('max', 10))+1):
			li = SubElement(ul, "li")
			inp = SubElement(li, "input", {
				"type": "radio",
				"name": "response" + str(qn),
				"value": str(n)
			})
			SubElement(li, "span").text = str(n)
		return div

	def get_preference(self, x, qn):
		div = Element("div", {
			"class": "question preference",
			"id": "question" + str(qn)
		})
		div.append(etree.XML("<h2>%s) %s</h2>" % (qn, x.find(NS['poll'] + "text").text)))

		for n, option in enumerate(x.find(NS['poll'] + "options").getchildren()):
			p = SubElement(div, "p")
			inp = SubElement(p, "input", {
				"type": "text",
				"name": "response%s-%s" % (qn, n+1)
			})
			SubElement(p, "span").text = option.text
		return div

