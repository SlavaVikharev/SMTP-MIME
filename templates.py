MESSAGE = """\
From: "%(from_name)s" <%(from_email)s>
To: "%(to_name)s" <%(to_email)s>
Subject: Images
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="%(boundary)s"

%(parts)s
--%(boundary)s--
."""


PART = """
--%(boundary)s
Content-Type: image/%(file_ext)s
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="%(filename)s"

%(body_part)s"""
