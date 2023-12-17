import functions_framework
import html
import io
import re
import typing
import urllib.request

from bs4 import BeautifulSoup
from typing import Generator


# Fetches the team members from the cradle.bio website.
# Returns a generator of tuples containing the name, role and image url
# (in that order).
def fetchTeamMembers() -> Generator[str | None, str | None, str | None]:
    with urllib.request.urlopen("http://cradle.bio/team") as response:
        soup = BeautifulSoup(response.read(), "html.parser")
        for div in soup.find_all("div", attrs={"class": re.compile("framer-\w+-container")}):
            yield div.find("h2").string, div.find("p").string, div.find("img")["src"]


# Generates the cradlers HTML file and returns its content.
def generateCradlers(out: typing.TextIO):
    card_template: str = open("templates/card_tmpl.html",
                              encoding="utf-8").read()
    page_header: str = open("templates/page_header.html",
                            encoding="utf-8").read()
    page_footer: str = open("templates/page_footer.html",
                            encoding="utf-8").read()

    out.write(page_header)
    for name, role, img in fetchTeamMembers():
        out.write(
            card_template.format(html.escape(img),
                                 html.escape(name),
                                 html.escape(role))
        )
    out.write(page_footer)


# If the script is run directly, we output the HTML to cradlers.html.
if __name__ == "__main__":
    with open("cradlers.html", "w", encoding="utf-8") as f:
        generateCradlers(f)
    exit(1)


# If the script is run as a Cloud Function, we output the HTML to the response.
@functions_framework.http
def get(request):
    response = io.StringIO()
    generateCradlers(response)
    return response.getvalue()
