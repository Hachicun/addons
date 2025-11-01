{
    "name": "Website Custom",
    "version": "18.0.1.0.0",
    "summary": "Code-first sample website: /landing page and assets",
    "depends": ["website"],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_custom/static/src/scss/styles.scss",
            "website_custom/static/src/js/main.js",
        ],
    },
    "installable": True,
    "application": False,
}
