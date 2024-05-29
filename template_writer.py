from argparse import ArgumentParser

import jinja2

template_filename_map = {
    '1': 'templates/service_template.j2',
    '2': 'templates/router_template.j2',
    '3': 'templates/schema_template.j2',
    'service': 'templates/service_template.j2',
    'router': 'templates/router_template.j2',
    'schema': 'templates/schema_template.j2'
}
output_dir_map = {
    '1': 'app/services/',
    '2': 'app/api/',
    '3': 'app/schemas/',
    'service': 'app/services/',
    'router': 'app/api/',
    'schema': 'app/schemas/'
}


def fill_template(template_filename, output_dir, name):
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    template = environment.get_template(template_filename)
    content = template.render(lower_name=name.lower(), name=name.capitalize())
    with open(output_dir + name + '.py', mode="w", encoding="utf-8") as f:
        f.write(content)
    print(f"Create {output_dir + name + '.py'}")


parser = ArgumentParser()
parser.add_argument('--name', '-n', type=str)
parser.add_argument('--template', '-t',
                    type=str,
                    help="""
                    Which template to use.
                    1 OR service - Service
                    2 OR router - Router(api)
                    3 OR schema - Schema
                    Default - all
                    """)
args = parser.parse_args()
if args.name is None:
    raise TypeError('Set --name argument')

if args.template:
    template_filename = template_filename_map.get(args.template.lower())
    output_dir = output_dir_map.get(args.template.lower())
    fill_template(template_filename, output_dir, args.name)
else:
    for template, output_dir in zip(list(template_filename_map.values())[:3], list(output_dir_map.values())[:3]):
        fill_template(template, output_dir, args.name)
