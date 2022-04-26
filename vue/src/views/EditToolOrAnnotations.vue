<template>
	<v-container>
		<EditTool
			v-if="tool_schema && tool && $can( 'change', tool )"
			:tool="tool"
			:tool-schema="tool_schema"
			:annotations-schema="annotations_schema"
			:links="links"
		/>
		<EditAnnotations
			v-else-if="annotations_schema &&
				tool &&
				!$can( 'change', tool ) &&
				$can( 'add', 'toolinfo/annotations' )"
			:tool="tool"
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
		...mapState( 'tools', [ 'tool' ] )
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
