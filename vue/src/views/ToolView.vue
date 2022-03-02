<template>
	<v-container>
		<v-row v-if="revId && toolRevision">
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
							(<a @click="patrol( toolRevision.id )">
								{{ $t( 'markaspatrolled' ) }}
							</a>)
						</template>
						<template v-else>
							(<span>{{ $t( 'patrolled' ) }}</span>)
						</template>
					</h3>
				</template>
			</v-col>
			<v-col md="3" cols="12">
				<v-btn
					:to="{ name: 'tools-history', params: { name: name } }"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtotoolhistory' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<ToolInfo
			:tool="( revId && toolRevision ) ? toolRevision.toolinfo : tool"
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
		return fetchMetaInfo( 'tools-view', this.name );
	},
	computed: {
		...mapState( 'tools', [ 'tool', 'toolRevision' ] )
	},
	methods: {
		...mapActions( 'tools', [ 'getToolByName', 'getToolRevision' ] ),
		...mapMutations( 'tools', [ 'TOOL', 'TOOL_REVISION' ] ),

		patrol( revId ) {
			this.$store.dispatch( 'tools/markRevisionAsPatrolled', {
				name: this.name,
				revId: revId,
				page: 1
			} ).then( () => {
				this.getToolInfo();
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
	mounted() {
		// Clear any data from a prior view
		this.TOOL( null );
		this.TOOL_REVISION( null );
		this.getToolInfo();
	}
};
</script>
