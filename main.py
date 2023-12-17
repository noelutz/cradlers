"""Generates a flip card HTML page to learn Cradlers' names.

Cradle is growing fast. It's hard to keep track of all the new faces.
This script fetches the list of Cradlers from the website and generates a
simple flip card HTML file that can be used to learn people's names.

The script can either be invoked locally to generate an HTML file that can
be served statically, or it can be deployed as a Cloud Function that will
generate the HTML on demand by fetching the list of Cradlers from the website.

Any bugs should be reported to noe@cradle.bio.
"""

import functions_framework
import html
import io
import re
import typing
import urllib.request

from bs4 import BeautifulSoup
from typing import Generator


def fetch_team_members() -> Generator[str | None, str | None, str | None]:
    """Fetches the team members from the cradle.bio website.

    Yields:
      A set of duples containing the name, role and image url (in that order).
    """
    with urllib.request.urlopen("http://cradle.bio/team") as response:
        soup = BeautifulSoup(response.read(), "html.parser")
        parent_div = soup.find("div", attrs={"name": "team grid"})
        for div in parent_div.find_all(
            "div", attrs={"class": re.compile("framer-.*-container")}
        ):
            yield div.find("h2").string, div.find("p").string, div.find("img")["src"]


def generate_cradlers(out: typing.TextIO):
    """Generates the cradlers HTML file and writes its content to out.

    Paremeters:
        out: The file to write the HTML to.
    """
    card_template: str = open("templates/card_tmpl.html", encoding="utf-8").read()
    page_header: str = open("templates/page_header.html", encoding="utf-8").read()
    page_footer: str = open("templates/page_footer.html", encoding="utf-8").read()

    out.write(page_header)
    for name, role, img in fetch_team_members():
        out.write(
            card_template.format(html.escape(img), html.escape(name), html.escape(role))
        )
    out.write(page_footer)


# If the script is run directly, we output the HTML to cradlers.html.
if __name__ == "__main__":
    with open("cradlers.html", "w", encoding="utf-8") as f:
        generate_cradlers(f)
    exit(1)


@functions_framework.http
def get(request):
    """The Cloud Function entry point. Generates the HTML and returns it.

    Parameters:
        request: The HTTP request. Not really used.
    """
    response = io.StringIO()
    generate_cradlers(response)
    return response.getvalue()
