# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Formation(models.Model):
    _name = "formation.formation"
    _description = "Formation"
    _order = "name, teacher_id, description"

    name = fields.Char("Name", required=True, track_visibility='onchange')
    date = fields.Date(string='Formation Date', track_visibility='onchange')
    teacher_id = fields.Many2one(comodel_name='res.partner', string='Teacher')
    description = fields.Text(help="add a description")
    student_ids = fields.Many2many('res.partner', 'formation_student_rel', 'formation_id', 'student_id', string='formations students')

class Teacher(models.Model):
    _inherit = 'res.partner'
    # ------------------------------------> Model de ref dans DB --- champ du model <-----------
    formation_taught_ids = fields.One2many('formation.formation', 'teacher_id', string="All my formations")
    # -------------------------------------->Model de ref ----- nom choisi pour la table commune --- nom choisi colonne de depart --- nom chois colomn de la foreign key -----
    formation_studied_ids = fields.Many2many('formation.formation', 'formation_student_rel', 'student_id', 'formation_id', string='formations attendee')

