# -*- coding: utf-8 -*-

from odoo import models, fields, api

import os
from google.cloud import vision
from google.cloud import language
from google.oauth2 import service_account
import json
import re
import base64
import logging
import io
logger = logging.getLogger(__name__)



class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def take_business_card_picture(self, picture_base64):
        google_api_json_file_content = self.env['ir.config_parameter'].sudo().get_param('google_api_json_file_content', default='')
        if not google_api_json_file_content:
            return
        service_account_info = json.loads(google_api_json_file_content)

        credentials = service_account.Credentials.from_service_account_info(service_account_info)

        vision_client = vision.ImageAnnotatorClient(credentials=credentials)

        image = vision.types.Image(content=base64.b64decode(picture_base64.split(",")[1]))

        # 1 unit consumed here
        response = vision_client.document_text_detection(image=image)
        logo_response = vision_client.logo_detection(image=image)

        card_text = response.full_text_annotation.text

        logos_text = [logo.description for logo in logo_response.logo_annotations]
        logo_text = logos_text and logos_text[0] or ''

        nl_client = language.LanguageServiceClient(credentials=credentials)
        document = language.types.Document(
            content=card_text,
            type=language.enums.Document.Type.PLAIN_TEXT
        )

        # 1 unit consumed here
        entities_result = nl_client.analyze_entities(document=document)

        # print(card_text, '\n\n\n')

        # for entity in entities_result.entities:
        #     entity_type = language.enums.Entity.Type(entity.type)
        #     print('=' * 20)
        #     print(u'{:<16}: {}'.format('name', entity.name))
        #     print(u'{:<16}: {}'.format('type', entity_type.name))
        #     print(u'{:<16}: {}'.format('salience', entity.salience))
        #     print(u'{:<16}: {}'.format('wikipedia_url',
        #           entity.metadata.get('wikipedia_url', '-')))
        #     print(u'{:<16}: {}'.format('mid', entity.metadata.get('mid', '-')))

        logger.info([(entity.name, language.enums.Entity.Type(entity.type).name, entity.metadata) for entity in entities_result.entities])
        logger.info(logo_text)

        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
        email_candidates = email_pattern.findall(card_text)
        logger.info(email_candidates)

