from pybtex.database.input import bibtex
import pybtex.database.input.bibtex
from time import strptime
import string
import html
import os
import re
import copy

myname = 'Satrajit Chakrabarty'
joint_first_authors = ['baheti2021brain'] # specify bib_ids where I am joint first author

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


publist = {"journal":{
        "file": "journal_entries.bib",
        "venuekey" : "journal",
        "venue-pretext" : "",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}},
        "conference":{
        "file": "conference_entries.bib",
        "venuekey" : "booktitle",
        "venue-pretext" : "In the proceedings of ",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}}
}

for pubsource in publist:
    parser = bibtex.Parser()
    bibdata = parser.parse_file(publist[pubsource]["file"])

    #loop through the individual references in a given bibtex file
    for bib_id in bibdata.entries:
        print(f"Now parsing {bib_id}")
        #reset default date
        pub_year = "1900"
        pub_month = "01"
        pub_day = "01"

        b = bibdata.entries[bib_id].fields

        try:
            pub_year = f'{b["year"]}'

            #todo: this hack for month and day needs some cleanup
            if "month" in b.keys():
                if(len(b["month"])<3):
                    pub_month = "0"+b["month"]
                    pub_month = pub_month[-2:]
                elif(b["month"] not in range(12)):
                    tmnth = strptime(b["month"][:3],'%b').tm_mon
                    pub_month = "{:02d}".format(tmnth)
                else:
                    pub_month = str(b["month"])
            if "day" in b.keys():
                pub_day = str(b["day"])


            pub_date = pub_year+"-"+pub_month+"-"+pub_day

            #strip out {} as needed (some bibtex entries that maintain formatting)
            clean_title = b["title"].replace("{", "").replace("}","").replace("\\","").replace(" ","-")

            url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
            url_slug = url_slug.replace("--","-")

            md_filename = f"{bib_id}.md"
            # bib_id
            html_filename = (str(pub_date) + "-" + url_slug).replace("--","-")

            #Build Citation from text
            citation = ""

            #citation authors - todo - add highlighting for primary author?
            for author in bibdata.entries[bib_id].persons["author"]:
                if author.last_names[0] != 'others':
                    citation = citation+" "+author.first_names[0]+" "+author.last_names[0]+","
                else:
                    citation = citation+" et al."

            auth_list = copy.deepcopy(citation).lstrip().rstrip().rstrip(',').split(', ')
            myname_idx = auth_list.index(myname)

            #citation title
            citation = citation + "\"" + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + ".\""

            #add venue logic depending on citation type
            venue = publist[pubsource]["venue-pretext"]+b[publist[pubsource]["venuekey"]].replace("{", "").replace("}","").replace("\\","")

            citation = citation + " " + html_escape(venue)
            citation = citation + ", " + pub_year + "."
            citation = citation.lstrip() # removing leading white space from left


            ## YAML variables
            md = "---\ntitle: \""   + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + '"\n'

            md += f"pubtype: '{html_escape(pubsource)}'\n"

            md += """collection: """ +  publist[pubsource]["collection"]["name"]

            md += """\npermalink: """ + publist[pubsource]["collection"]["permalink"]  + bib_id

            note = False
            if "note" in b.keys():
                if len(str(b["note"])) > 5:
                    md += "\nexcerpt: '" + html_escape(b["note"]) + "'"
                    note = True

            md += "\ndate: " + str(pub_date)

            md += "\nvenue: '" + html_escape(venue) + "'"

            url = False
            if "url" in b.keys():
                if len(str(b["url"])) > 5:
                    md += "\npaperurl: '" + b["url"] + "'"
                    url = True

            md += "\ncitation: '" + html_escape(citation) + "'"

            md += "\n---"


            ## Markdown description for individual page
            scholar_link = f'(https://scholar.google.com/scholar?q={html.escape(clean_title.replace("-","+"))}){{:target=\"_blank\"}}'
            auth_list[myname_idx] = f"<ins>{myname}</ins>"

            # check for joint first author
            if bib_id in joint_first_authors: auth_list = [f"{i}\*" if idx <= myname_idx else i for idx, i in enumerate(auth_list) ]
            auth_list = ", ".join(auth_list).rstrip(', ')

            md += f"\n[{b['title']}]{scholar_link}<br />\n"
            md += f"{auth_list} <br />\n"
            if bib_id in joint_first_authors: md += f"*_Equally contributing first authors_ <br />\n"
            md += f"{venue}, {pub_year}."

            # Writing  to md file
            md_filename = os.path.basename(md_filename)

            with open("../_publications/" + md_filename, 'w') as f:
            # with open(md_filename, 'w') as f:
                f.write(md)
            print(f'SUCESSFULLY PARSED {bib_id}: \"', b["title"][:60],"..."*(len(b['title'])>60),"\"")
        # field may not exist for a reference
        except KeyError as e:
            print(f'WARNING Missing Expected Field {e} from entry {bib_id}: \"', b["title"][:30],"..."*(len(b['title'])>30),"\"")
            continue
