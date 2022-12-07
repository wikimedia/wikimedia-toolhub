<template>
	<v-container>
		<EditTool
			v-if="editToolinfo &&
				tool_schema &&
				tool &&
				$can( 'change', tool )"
			:tool="tool"
			:tool-schema="tool_schema"
			:annotations-schema="annotations_schema"
			:links="links"
		/>
		<EditAnnotations
			v-else-if="editAnnotations &&
				annotations_schema &&
				tool &&
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

import fetchMetaInfo from '@/helpers/metadata';

import EditAnnotations from '@/components/tools/EditAnnotations';
import EditTool from '@/components/tools/EditTool';
import ScrollTop from '@/components/common/ScrollTop';

const EDIT_TOOL = 'edit';
const EDIT_ANNOTATIONS = 'edit-annotations';

export default {
	name: 'EditToolOrAnnotations',
	components: {
		EditTool,
		EditAnnotations,
		ScrollTop
	},
	data() {
		return {
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
		...mapState( 'tools', [ 'tool' ] ),
		name() {
			return this.$route.params.name;
		},
		editType() {
			return this.$route.path.split( '/' ).pop();
		},
		editToolinfo() {
			return this.editType === EDIT_TOOL;
		},
		editAnnotations() {
			return this.editType === EDIT_ANNOTATIONS;
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
