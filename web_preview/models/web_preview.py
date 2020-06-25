import re

from odoo import api, fields, models


class Preview(models.AbstractModel):
    _name = "web.preview"

    media_type = fields.Char("Type", compute="_compute_type")
    media_video_ID = fields.Char("Video ID", compute="_compute_video_ID")
    media_video_service = fields.Char("Video Service", compute="_compute_video_service")

    @api.multi
    def _compute_type(self):
        for r in self:
            attachment = self.env["ir.attachment"]
            att = attachment.search(
                [
                    ("res_model", "=", self._name),
                    ("res_field", "=", r._preview_media_file),
                    ("res_id", "=", r.id),
                ]
            )
            if (
                att.mimetype == "application/octet-stream"
                and att.url
                and (
                    self.youtube_url_validation(att.url)
                    or self.vimeo_url_validation(att.url)
                )
            ):
                r.media_type = "video/url"
            else:
                r.media_type = att.mimetype

    @api.multi
    def _compute_video_ID(self):
        for r in self:
            attachment = self.env["ir.attachment"]
            att = attachment.search(
                [
                    ("res_model", "=", self._name),
                    ("res_field", "=", r._preview_media_file),
                    ("res_id", "=", r.id),
                ]
            )
            if att.mimetype == "application/octet-stream" and att.url:
                r.media_video_ID = self.youtube_url_validation(
                    att.url
                ) or self.vimeo_url_validation(att.url)

    @api.multi
    def _compute_video_service(self):
        for r in self:
            attachment = self.env["ir.attachment"]
            att = attachment.search(
                [
                    ("res_model", "=", self._name),
                    ("res_field", "=", r._preview_media_file),
                    ("res_id", "=", r.id),
                ]
            )
            if att.mimetype == "application/octet-stream" and att.url:
                if self.youtube_url_validation(att.url):
                    r.media_video_service = "youtube"
                elif self.vimeo_url_validation(att.url):
                    r.media_video_service = "vimeo"

    def youtube_url_validation(self, url):
        youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
        youtube_regex_match = re.match(youtube_regex, url)
        if youtube_regex_match:
            return youtube_regex_match.group(6)
        return youtube_regex_match

    def vimeo_url_validation(self, url):
        vimeo_regex = r"(https?://)?(www\.)?(vimeo\.com/)?(\d+)"
        vimeo_regex_match = re.match(vimeo_regex, url)
        if vimeo_regex_match:
            return vimeo_regex_match.group(4)
        return vimeo_regex_match
