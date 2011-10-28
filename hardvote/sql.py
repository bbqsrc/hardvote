import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import Column, Integer, String, create_engine

Base = declarative_base()
class Response(Base):
	__tablename__ = "responses"
	
	id = Column(Integer, primary_key=True)
	user_uuid = Column(String(50))
	poll_id = Column(String(50)) # checksum
	question_id = Column(Integer)
	response_id = Column(Integer)
	response = Column(String)

	def __init__(self, user_uuid, poll_id, question_id, response_id, response=None):
		self.user_uuid = user_uuid
		self.poll_id = poll_id
		self.question_id = int(question_id)
		self.response_id = int(response_id)
		if response:
			self.response = response

class SQLHandler(object):
	def __init__(self, config):
		self.Session = sessionmaker()

		self.engine = create_engine(config, echo=True)
		self.Session.configure(bind=self.engine)
		self.session = self.Session()
		Base.metadata.create_all(self.engine)

	def user_exists_in_table(self, uuid_hex):
		try:
			x = self.session.query(Response).filter(Response.user_uuid==uuid_hex).first()
			if not x:
				return False
			return True
		except Exception as e:
			print(e)
			return True

	def add_responses(self, responses):
		try:
			self.session.add_all(responses)
			self.session.commit()

		except Exception as e:
			# XXX use logging here
			print(e)
			self.session.rollback()
			return

