import logging
import re

# ------------------------------------------------------------------------------- #


def template(body, domain):
    BUG_REPORT = 'Cloudflare may have changed their technique, or there may be a bug in the script.'

    try:
        js = re.search(
            r'setTimeout\(function\(\){\s+(.*?a\.value\s*=\s*\S+toFixed\(10\);)',
            body,
            re.M | re.S,
        )[1]
    except Exception:
        raise ValueError(
            f'Unable to identify Cloudflare IUAM Javascript on website. {BUG_REPORT}'
        )

    jsEnv = '''String.prototype.italics=function(str) {{return "<i>" + this + "</i>";}};
        var subVars= {{{subVars}}};
        var document = {{
            createElement: function () {{
                return {{ firstChild: {{ href: "https://{domain}/" }} }}
            }},
            getElementById: function (str) {{
                return {{"innerHTML": subVars[str]}};
            }}
        }};
    '''

    try:
        js = js.replace(
            r"(setInterval(function(){}, 100),t.match(/https?:\/\//)[0]);",
            r"t.match(/https?:\/\//)[0];"
        )

        k = re.search(r" k\s*=\s*'(?P<k>\S+)';", body)['k']
        r = re.compile(f'<div id="{k}(?P<id>\d+)">\s*(?P<jsfuck>[^<>]*)</div>')

        subVars = ''
        for m in r.finditer(body):
            subVars = f"{subVars}\n\t\t{k}{m.group('id')}: {m.group('jsfuck')},\n"
        subVars = subVars[:-2]

    except:  # noqa
        logging.error(f'Error extracting Cloudflare IUAM Javascript. {BUG_REPORT}')
        raise

    return '{}{}'.format(
        re.sub(
            r'\s{2,}',
            ' ',
            jsEnv.format(
                domain=domain,
                subVars=subVars
            ),
            re.MULTILINE | re.DOTALL
        ),
        js
    )

# ------------------------------------------------------------------------------- #
