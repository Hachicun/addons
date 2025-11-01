# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LucKhiTeamMember(models.Model):
    _name = 'luc_khi.team.member'
    _description = 'Lục Khí Team Member'
    _order = 'sequence, name'
    
    name = fields.Char('Name', required=True, translate=True)
    position = fields.Char('Position', translate=True)
    bio = fields.Html('Biography', translate=True)
    
    # Media
    photo = fields.Image('Photo')
    
    # Contact
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    zalo = fields.Char('Zalo')
    
    # Expertise
    expertise = fields.Text('Areas of Expertise', translate=True)
    certifications = fields.Text('Certifications', translate=True)
    
    # Display
    is_published = fields.Boolean('Published', default=True)
    sequence = fields.Integer('Sequence', default=10)
    featured = fields.Boolean('Featured Member', default=False)
    
    def toggle_published(self):
        """Toggle the published status of team members"""
        for record in self:
            record.is_published = not record.is_published

    def toggle_featured(self):
        """Toggle the featured status of team members"""
        for record in self:
            record.featured = not record.featured

    def action_view_website(self):
        """View member profile on website"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/team/{self.id}',
            'target': 'new',
        }