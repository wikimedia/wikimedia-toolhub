<template>
	<v-container>
		<v-row v-if="toolRevision">
			<v-col md="9" cols="12">
				<h3 class="font-weight-medium">
					{{ $t( 'toolrevisioninfo', [
						toolRevision.timestamp,
						toolRevision.user.username,
						toolRevision.comment
					] ) }}
				</h3>
				<template v-if="$can( 'patrol', 'reversion/version' )">
					<h3 class="font-weight-medium">
						<template v-if="!toolRevision.patrolled">
							(<a @click="patrol(toolRevision.id)">{{ $t( 'markaspatrolled' ) }}</a>)
						</template>
						<template v-else>
							(<span>{{ $t( 'patrolled' ) }}</span>)
						</template>
					</h3>
				</template>
			</v-col>
			<v-col md="3" cols="12">
				<v-btn
					:to="`/tool/${name}`"
					:small="$vuetify.breakpoint.smAndDown"
					@click="backToToolInfo"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtotoolinfo' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<ToolInfo
			:tool="revId ? toolRevision && toolRevision.toolinfo : tool"
			:rev-id="revId"
			:name="name"
		/>
	</v-container>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';
import ToolInfo from '@/components/tools/ToolInfo';
import fetchMetaInfo from '@/helpers/metadata';

export default {
	name: 'ToolView',
	components: {
		ToolInfo
	},
	data() {
		return {
			name: this.$route.params.name,
			revId: this.$route.params.revId
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'toolview', this.name );
	},
	computed: {
		...mapState( 'tools', [ 'tool', 'toolRevision' ] )
	},
	methods: {
		...mapActions( 'tools', [ 'getToolByName', 'getToolRevision' ] ),
		...mapMutations( 'tools', [ 'TOOL', 'TOOL_REVISION' ] ),

		formatDate( date ) {
			return this.$moment.utc( date ).format( 'LT ll' );
		},
		backToToolInfo() {
			this.revId = null;
			this.TOOL_REVISION( null );
			this.getToolByName( this.name );
		},
		patrol( id ) {
			this.$store.dispatch( 'tools/markRevisionAsPatrolled', {
				name: this.name,
				id: id,
				page: 1
			} );
		},
		getToolInfo() {
			if ( this.revId ) {
				this.getToolRevision( { name: this.name, revId: this.revId } );
			} else {
				this.getToolByName( this.name );
			}
		}
	},
	watch: {
		toolRevision: {
			handler() {
				this.getToolInfo();
			}
		}
	},
	mounted() {
		// Clear any data from a prior view
		this.TOOL( null );
		this.TOOL_REVISION( null );
		this.getToolInfo();
	}
};
</script>
