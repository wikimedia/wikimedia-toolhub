<template>
	<v-container>
		<EditTool
			v-if="tool_schema && toolFromVuex && $can( 'change', tool )"
			v-model="tool"
			:tool-schema="tool_schema"
			:annotations-schema="annotations_schema"
			:links="links"
		/>
		<EditAnnotations
			v-else-if="annotations_schema &&
				toolFromVuex &&
				!$can( 'change', tool ) &&
				$can( 'add', 'toolinfo/annotations' )"
			v-model="tool"
			:schema="annotations_schema"
			:links="links"
		/>
		<v-row>
			<v-col cols="12">
				<ScrollTop />
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import EditTool from '@/components/tools/EditTool';
import EditAnnotations from '@/components/tools/EditAnnotations';
import ScrollTop from '@/components/common/ScrollTop';
import fetchMetaInfo from '@/helpers/metadata';
import { asTool } from '@/helpers/casl';

export default {
	name: 'EditToolOrAnnotations',
	components: {
		EditTool,
		EditAnnotations,
		ScrollTop
	},
	data() {
		return {
			name: this.$route.params.name,
			links: [
				'user_docs_url',
				'developer_docs_url',
				'privacy_policy_url',
				'feedback_url',
				'url_alternates'
			]
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'tools-edit', this.name );
	},
	computed: {
		...mapState( 'tools', { toolFromVuex: 'tool' } ),
		tool() {
			// Deep clone state from vuex so that we can pass it as a v-model.
			return asTool( JSON.parse( JSON.stringify( this.toolFromVuex ) ) );
		}
	},
	asyncComputed: {
		tool_schema: {
			get() {
				return this.getRequestSchema( 'tools_update' );
			},
			default: false
		},
		annotations_schema: {
			get() {
				return this.getRequestSchema( 'tools_annotations_update' );
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getRequestSchema' ] ),
		...mapActions( 'tools', [ 'getToolByName' ] )
	},
	mounted() {
		this.getToolByName( this.name );
	}
};
</script>
