# -*- coding: utf-8 -*-
{
    'name': "Grid View extension",

    'summary': "",
    'description': """
Adds the ability to show a custom action and do extra
processing when clicking on the cell lens on the grid view input:
Simply override the method show_grid_cell and return an action inside it  
inside your model
    """,

    'version': '0.1',
    'depends': ['web_grid'],

    'data': ['views/templates.xml'],

}
