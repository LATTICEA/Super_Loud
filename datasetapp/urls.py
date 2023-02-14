from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('datasets', subscriptions, name='subscriptions')
    , path('delete-dataset/<int:id>', delete_dataset, name='delete-dataset')
    , path('get-graph-values/<str:area>/<str:industry>/<str:occupation>/<str:skills>', get_graph_values, name='get-graph-values')
    # , path('get-graph-values/<str:area>/<str:industry>/<str:occupation>', get_graph_values, name='get-graph-values')
    , path('graph-disco/<str:area_id>/<str:industry_id>/<str:msa_county>', graph_disco, name='graph-disco')
    , path('graph-disco-create/<str:area_id>/<str:skills>', graph_disco_create, name='graph-disco-create')
    , path('graph-disco-occ/<str:area_id>/<str:industry_id>/<str:msa_county>/<str:occupation_id>', graph_disco_occ, name='graph-disco-occ')
    , path('graph-bands/<str:area_id>/<str:industry_id>/<str:msa_county>/<str:occupation_id>', graph_bands, name='graph-bands')

    , path('get-areas-from-state/<str:state>', get_areas_from_state)
    , path('get-msa-from-state/<str:state>', get_msa_from_state)
    , path('get-industries-from-area/<str:area>', get_industries_from_area)
    , path('get-industries-from-msa/<str:msa>', get_industries_from_msa)

    , path('get-occupations-from-msa/<str:msa>/<str:industry>', get_occupation_from_msa)

    , path('get-skills-from-county/<str:county>', get_skills_from_county)
    , path('get-skills-from-msa/<str:msa>', get_skills_from_msa)
]

urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)