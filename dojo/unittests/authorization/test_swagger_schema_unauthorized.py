from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.test import APITestCase, force_authenticate, APIClient
from rest_framework.mixins import \
    RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework import status
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.openapi import Info

from dojo.api_v2.views import \
    DevelopmentEnvironmentViewSet, EndpointStatusViewSet, EndPointViewSet, \
    EngagementViewSet, FindingTemplatesViewSet, FindingViewSet, \
    JiraInstanceViewSet, DojoMetaViewSet, NoteTypeViewSet, NotesViewSet, \
    ProductTypeViewSet, ProductViewSet, RegulationsViewSet, \
    SonarqubeIssueViewSet, SonarqubeProductViewSet, \
    SonarqubeIssueTransitionViewSet, StubFindingsViewSet, SystemSettingsViewSet, \
    TestTypesViewSet, TestsViewSet, ToolConfigurationsViewSet, ToolProductSettingsViewSet, \
    ToolTypesViewSet, UsersViewSet, JiraIssuesViewSet, JiraProjectViewSet, AppAnalysisViewSet

from dojo.models import \
    Development_Environment, Endpoint_Status, Endpoint, Engagement, Finding_Template, \
    Finding, JIRA_Instance, JIRA_Issue, DojoMeta, Note_Type, Notes, Product_Type, Product, Regulation, \
    Sonarqube_Issue, Sonarqube_Product, Sonarqube_Issue_Transition, \
    Stub_Finding, System_Settings, Test_Type, Test, Tool_Configuration, Tool_Product_Settings, \
    Tool_Type, Dojo_User, JIRA_Project, App_Analysis

from dojo.api_v2.serializers import \
    DevelopmentEnvironmentSerializer, EndpointStatusSerializer, EndpointSerializer, \
    EngagementSerializer, FindingTemplateSerializer, FindingSerializer, \
    JIRAInstanceSerializer, JIRAIssueSerializer, JIRAProjectSerializer, MetaSerializer, NoteTypeSerializer, \
    ProductSerializer, RegulationSerializer, \
    SonarqubeIssueSerializer, SonarqubeProductSerializer, SonarqubeIssueTransitionSerializer, \
    StubFindingSerializer, SystemSettingsSerializer, TestTypeSerializer, TestSerializer, ToolConfigurationSerializer, \
    ToolProductSettingsSerializer, ToolTypeSerializer, UserSerializer, NoteSerializer, ProductTypeSerializer, \
    AppAnalysisSerializer

from dojo.unittests.test_swagger_schema import BaseClass, testIsBroken, skipIfNotSubclass, check_response_valid, format_url

SWAGGER_SCHEMA_GENERATOR = OpenAPISchemaGenerator(Info("defectdojo", "v2"))
BASE_API_URL = "/api/v2"


class BaseClassUnauthorized(BaseClass):
    class SchemaTest(APITestCase):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.user is None

        def setUp(self):
            super().setUp()
            self.user = Dojo_User()
            self.user.id = 2

            factory = APIRequestFactory()
            request = factory.get('/')
            force_authenticate(request, user=self.user)
            request = APIView().initialize_request(request)

            self.schema = SWAGGER_SCHEMA_GENERATOR.get_schema(request, public=True)
            self.client = APIClient()
            self.client.force_authenticate(user=self.user)

        @skipIfNotSubclass(ListModelMixin)
        def test_list_endpoint(self, extra_args=None):
            endpoints = self.schema["paths"][f"/{self.viewname}/"]
            response = self.client.get(format_url(f"/{self.viewname}/"), extra_args)
            check_response_valid(status.HTTP_403_FORBIDDEN, response)

            schema = endpoints['get']['responses']['403']['schema']
            obj = response.data

            self.check_schema(schema, obj)

        @skipIfNotSubclass(RetrieveModelMixin)
        def test_retrieve_endpoint(self, extra_args=None):
            endpoints = self.schema["paths"][f"/{self.viewname}/{{id}}/"]
            response = self.client.get(format_url(f"/{self.viewname}/"))
            check_response_valid(status.HTTP_200_OK, response)
            ids = [obj['id'] for obj in response.data["results"]]

            schema = endpoints['get']['responses']['403']['schema']
            for id in ids:
                response = self.client.get(format_url(f"/{self.viewname}/{id}/"), extra_args)
                check_response_valid(status.HTTP_403_FORBIDDEN, response)
                obj = response.data
                self.check_schema(schema, obj)

        @skipIfNotSubclass(UpdateModelMixin)
        def test_patch_endpoint(self, extra_args=None):
            operation = self.schema["paths"][f"/{self.viewname}/{{id}}/"]["patch"]

            id = self.get_valid_object_id()
            if id is None:
                self.skipTest("No data exists to test endpoint")

            data = self.construct_response_data(id)

            schema = operation['responses']['403']['schema']
            response = self.client.patch(format_url(f"/{self.viewname}/{id}/"), data, format='json')
            check_response_valid(status.HTTP_200_OK, response)

            obj = response.data
            self.check_schema(schema, obj)

        @skipIfNotSubclass(UpdateModelMixin)
        def test_put_endpoint(self, extra_args=None):
            operation = self.schema["paths"][f"/{self.viewname}/{{id}}/"]['put']

            id = self.get_valid_object_id()
            if id is None:
                self.skipTest("No data exists to test endpoint")

            data = self.construct_response_data(id)

            schema = operation['responses']['403']['schema']
            response = self.client.put(format_url(f"/{self.viewname}/{id}/"), data, format='json')
            check_response_valid(status.HTTP_403_FORBIDDEN, response)

            obj = response.data
            self.check_schema(schema, obj)

        @skipIfNotSubclass(CreateModelMixin)
        def test_post_endpoint(self, extra_args=None):
            operation = self.schema["paths"][f"/{self.viewname}/"]["post"]

            id = self.get_valid_object_id()
            if id is None:
                self.skipTest("No data exists to test endpoint")

            data = self.construct_response_data(id)

            schema = operation['responses']['201']['schema']
            response = self.client.post(format_url(f"/{self.viewname}/"), data, format='json')
            check_response_valid(status.HTTP_403_FORBIDDEN, response)

            obj = response.data
            self.check_schema(schema, obj)


class DevelopmentEnvironmentTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "development_environments"
        self.viewset = DevelopmentEnvironmentViewSet
        self.model = Development_Environment
        self.serializer = DevelopmentEnvironmentSerializer


# Test will only work when FEATURE_AUTHENTICATION_V2 is the default
# class DojoGroupTest(BaseClass.SchemaTest):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.viewname = "dojo_groups"
#         self.viewset = DojoGroupViewSet
#         self.model = Dojo_Group
#         self.serializer = DojoGroupSerializer


class EndpointStatusTest(BaseClassUnauthorized.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "endpoint_status"
        self.viewset = EndpointStatusViewSet
        self.model = Endpoint_Status
        self.serializer = EndpointStatusSerializer


class EndpointTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "endpoints"
        self.viewset = EndPointViewSet
        self.model = Endpoint
        self.serializer = EndpointSerializer
        self.field_transformers = {
            "path": lambda v: (v if v else '') + "transformed/"
        }


class EngagementTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "engagements"
        self.viewset = EngagementViewSet
        self.model = Engagement
        self.serializer = EngagementSerializer

    @testIsBroken
    def test_accept_risks(self):
        operation = self.get_endpoint_schema("/engagements/{id}/accept_risks/", "post")
        schema = operation['responses']['201']['schema']
        id = self.get_valid_object_id()
        if id is None:
            self.skipTest("No data exists to test endpoint")

        data = [
            {
                "cve": 1,
                "justification": "test",
                "accepted_by": "2"
            }
        ]

        response = self.client.post(format_url(f"/engagements/{id}/accept_risks/"), data, format='json')
        check_response_valid(201, response)
        obj = response.data
        self.check_schema(schema, obj)

    @testIsBroken
    def test_notes_read(self):
        operation = self.get_endpoint_schema("/engagements/{id}/notes/", "get")
        schema = operation['responses']['200']['schema']
        id = self.get_valid_object_id()
        if id is None:
            self.skipTest("No data exists to test endpoint")

        response = self.client.get(format_url(f"/engagements/{id}/notes/"))
        check_response_valid(200, response)
        obj = response.data
        self.check_schema(schema, obj)

    @testIsBroken
    def test_notes_create(self):
        operation = self.get_endpoint_schema("/engagements/{id}/notes/", "post")
        schema = operation['responses']['201']['schema']
        id = self.get_valid_object_id()
        if id is None:
            self.skipTest("No data exists to test endpoint")

        data = {
            "entry": "test",
            "author": 2,
        }

        response = self.client.post(format_url(f"/engagements/{id}/notes/"), data, format='json')
        check_response_valid(201, response)
        obj = response.data
        self.check_schema(schema, obj)


class FindingTemplateTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "finding_templates"
        self.viewset = FindingTemplatesViewSet
        self.model = Finding_Template
        self.serializer = FindingTemplateSerializer

    @testIsBroken
    def test_post_endpoint(self):
        super().test_post_endpoint()

    @testIsBroken
    def test_patch_endpoint(self):
        super().test_patch_endpoint()

    @testIsBroken
    def test_put_endpoint(self):
        super().test_put_endpoint()


class FindingTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "findings"
        self.viewset = FindingViewSet
        self.model = Finding
        self.serializer = FindingSerializer

    @testIsBroken
    def test_list_endpoint(self):
        super().test_list_endpoint({
            "related_fields": True
        })

    @testIsBroken
    def test_patch_endpoint(self):
        super().test_patch_endpoint()

    @testIsBroken
    def test_put_endpoint(self):
        super().test_put_endpoint()

    @testIsBroken
    def test_retrieve_endpoint(self):
        super().test_retrieve_endpoint({
            "related_fields": True
        })


class JiraInstanceTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "jira_instances"
        self.viewset = JiraInstanceViewSet
        self.model = JIRA_Instance
        self.serializer = JIRAInstanceSerializer

    @testIsBroken
    def test_list_endpoint(self):
        super().test_list_endpoint()

    @testIsBroken
    def test_patch_endpoint(self):
        super().test_patch_endpoint()

    @testIsBroken
    def test_put_endpoint(self):
        super().test_put_endpoint()

    @testIsBroken
    def test_retrieve_endpoint(self):
        super().test_retrieve_endpoint()

    @testIsBroken
    def test_post_endpoint(self):
        super().test_post_endpoint()


class JiraFindingMappingsTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "jira_finding_mappings"
        self.viewset = JiraIssuesViewSet
        self.model = JIRA_Issue
        self.serializer = JIRAIssueSerializer
        self.field_transformers = {
            "finding": lambda v: 2,
            "engagement": lambda v: 2
        }


class JiraProjectTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "jira_projects"
        self.viewset = JiraProjectViewSet
        self.model = JIRA_Project
        self.serializer = JIRAProjectSerializer


class MetadataTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "metadata"
        self.viewset = DojoMetaViewSet
        self.model = DojoMeta
        self.serializer = MetaSerializer


class NoteTypeTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "note_type"
        self.viewset = NoteTypeViewSet
        self.model = Note_Type
        self.serializer = NoteTypeSerializer
        self.field_transformers = {
            "name": lambda v: v + "_new"
        }


class NoteTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "notes"
        self.viewset = NotesViewSet
        self.model = Notes
        self.serializer = NoteSerializer


class ProductTypeTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "product_types"
        self.viewset = ProductTypeViewSet
        self.model = Product_Type
        self.serializer = ProductTypeSerializer
        self.field_transformers = {
            "name": lambda v: v + "_new"
        }


# Test will only work when FEATURE_AUTHENTICATION_V2 is the default
# class ProductTypeMemberTest(BaseClass.SchemaTest):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.viewname = "product_type_members"
#         self.viewset = ProductTypeMemberViewSet
#         self.model = Product_Type_Member
#         self.serializer = ProductTypeMemberSerializer


# Test will only work when FEATURE_AUTHENTICATION_V2 is the default
# class ProductTypeGroupTest(BaseClass.SchemaTest):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.viewname = "product_type_groups"
#         self.viewset = ProductTypeGroupViewSet
#         self.model = Product_Type_Group
#         self.serializer = ProductTypeGroupSerializer


class ProductTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "products"
        self.viewset = ProductViewSet
        self.model = Product
        self.serializer = ProductSerializer
        self.field_transformers = {
            "name": lambda v: v + "_new"
        }

    @testIsBroken
    def test_list_endpoint(self):
        super().test_list_endpoint()

    @testIsBroken
    def test_patch_endpoint(self):
        super().test_patch_endpoint()

    @testIsBroken
    def test_put_endpoint(self):
        super().test_put_endpoint()

    @testIsBroken
    def test_retrieve_endpoint(self):
        super().test_retrieve_endpoint()

    @testIsBroken
    def test_post_endpoint(self):
        super().test_post_endpoint()


# Test will only work when FEATURE_AUTHENTICATION_V2 is the default
# class ProductMemberTest(BaseClass.SchemaTest):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.viewname = "product_members"
#         self.viewset = ProductMemberViewSet
#         self.model = Product_Member
#         self.serializer = ProductMemberSerializer

#     @testIsBroken
#     def test_post_endpoint(self):
#         super().test_post_endpoint()

#     @testIsBroken
#     def test_patch_endpoint(self):
#         super().test_post_endpoint()


# Test will only work when FEATURE_AUTHENTICATION_V2 is the default
# class ProductGroupTest(BaseClass.SchemaTest):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.viewname = "product_groups"
#         self.viewset = ProductGroupViewSet
#         self.model = Product_Group
#         self.serializer = ProductGroupSerializer


class RegulationTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "regulations"
        self.viewset = RegulationsViewSet
        self.model = Regulation
        self.serializer = RegulationSerializer


class SonarqubeIssuesTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "sonarqube_issues"
        self.viewset = SonarqubeIssueViewSet
        self.model = Sonarqube_Issue
        self.serializer = SonarqubeIssueSerializer
        self.field_transformers = {
            "key": lambda v: v + "_new"
        }


class SonarqubeProductConfTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "sonarqube_product_configurations"
        self.viewset = SonarqubeProductViewSet
        self.model = Sonarqube_Product
        self.serializer = SonarqubeProductSerializer


class SonarqubeTransitionTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "sonarqube_transitions"
        self.viewset = SonarqubeIssueTransitionViewSet
        self.model = Sonarqube_Issue_Transition
        self.serializer = SonarqubeIssueTransitionSerializer


class StubFindingTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "stub_findings"
        self.viewset = StubFindingsViewSet
        self.model = Stub_Finding
        self.serializer = StubFindingSerializer


class SystemSettingTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "system_settings"
        self.viewset = SystemSettingsViewSet
        self.model = System_Settings
        self.serializer = SystemSettingsSerializer


class AppAnalysisTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "technologies"
        self.viewset = AppAnalysisViewSet
        self.model = App_Analysis
        self.serializer = AppAnalysisSerializer

    @testIsBroken
    def test_patch_endpoint(self):
        super().test_patch_endpoint()

    @testIsBroken
    def test_put_endpoint(self):
        super().test_put_endpoint()

    @testIsBroken
    def test_post_endpoint(self):
        super().test_post_endpoint()


class TestTypeTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "test_types"
        self.viewset = TestTypesViewSet
        self.model = Test_Type
        self.serializer = TestTypeSerializer
        self.field_transformers = {
            "name": lambda v: v + "_new"
        }


class TestsTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "tests"
        self.viewset = TestsViewSet
        self.model = Test
        self.serializer = TestSerializer


class ToolConfigurationTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "tool_configurations"
        self.viewset = ToolConfigurationsViewSet
        self.model = Tool_Configuration
        self.serializer = ToolConfigurationSerializer


class ToolProductSettingTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "tool_product_settings"
        self.viewset = ToolProductSettingsViewSet
        self.model = Tool_Product_Settings
        self.serializer = ToolProductSettingsSerializer


class ToolTypeTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "tool_types"
        self.viewset = ToolTypesViewSet
        self.model = Tool_Type
        self.serializer = ToolTypeSerializer


class UserTest(BaseClass.SchemaTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewname = "users"
        self.viewset = UsersViewSet
        self.model = Dojo_User
        self.serializer = UserSerializer
        self.field_transformers = {
            "username": lambda v: v + "_transformed"
        }
