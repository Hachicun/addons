# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LucKhiCourseTag(models.Model):
    _name = 'luc_khi.course.tag'
    _description = 'Course Tag'
    _order = 'name'
    
    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=0)
    course_ids = fields.Many2many('luc_khi.course', column_name='course_tag_rel')
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!'),
    ]
    
    def action_view_courses(self):
        """View all courses with this tag"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Courses with tag: {self.name}',
            'res_model': 'luc_khi.course',
            'domain': [('tag_ids', 'in', [self.id])],
            'view_mode': 'tree,form',
        }