import json
import re

import frappe
import frappe.sessions
from frappe.utils import cint

no_cache = 1
login_required = True

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosemgrep

	try:
		boot = frappe.sessions.get()
	except Exception as e:
		raise frappe.SessionBootFailed from e

	if "server_script_enabled" in frappe.conf:
		enabled = frappe.conf.server_script_enabled
	else:
		enabled = True
	boot["server_script_enabled"] = enabled

	boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = json.dumps(boot_json)

	context.update(
		{
			"build_version": frappe.utils.get_build_version(),
			"boot": boot_json,
			"csrf_token": csrf_token,
			"dev_server": cint(getattr(frappe.local, "dev_server", 0)),
		}
	)
	return context
