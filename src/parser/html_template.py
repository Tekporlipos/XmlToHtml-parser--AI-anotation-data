html_template = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Kwame-source-case-template</title>
  </head>
  <body>
    <section id="metadata">
      <div id="title">
       {{ title }}
      </div>
      <div id="date">
       {{ date }}
      </div>
      <div id="caseId">
       {{ case_id }}
      </div>
      <div id="refId">
        {{ refId }}
      </div>
      <div id="court">
       {{ court }}
        {{court_location}}
        </div>
      <div id="judges">
        {{ judges }}
      </div>
      <div id="presiding-judge">
        {{ presiding_judge }}
      </div>
      <div id="parties">
      {{parties}}
      </div>
      <div id="counsel">
       {{counsel}}
      </div>
      <div id="media-nuetral-citation">
      {{media_nuetral_citation}}
      </div>
      <div id="law-report-citation">
       {{law_report_citation}}
      </div>
      <div id="indices">
       {{indices}}
      </div>
      <div id="source">
        {{source}}
      </div>
      <div id="nature-of-proceedings">
        {{nature_of_proceedings}}
      </div>
      <div id="headnotes">
      {{headnotes}}
      </div>
      <div id="editorial-notes">
       {{editorial_notes}}
      </div>
      <div id="books-referred-to">
        {{ books_referred_to }}
      </div>
        <div id="cases-referred-to">
        {{cases_referred_to}}
      </div>
      <div id="statutes-referred-to">
        {{statutes_referred_to}}
      </div>
      <div id="footnotes">
        {{footnotes}}
      </div>
    </section>
    <div id="documentType">
      {{documentType}}
    </div>
    <section id="content">
      {{content}}
    </section>
  </body>
</html>"""