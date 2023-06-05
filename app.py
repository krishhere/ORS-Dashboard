import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
                                                                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])
#server = app.server

navbar = dbc.NavbarSimple(
    dbc.Nav(
        [dbc.NavLink(page["name"], href=page["path"],class_name="nav-link scrollto",style={'color':'white'})
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],class_name="navbar"
    ),brand="ORS Dashboard", color="primary", dark=True,className="container",style={'max-width':'100%'}
)

app.layout = dbc.Container(
    [navbar, dash.page_container],
    fluid=True,class_name="bg-dark text-white"
)

if __name__ == "__main__":
    app.run_server(debug=True,dev_tools_hot_reload=False)