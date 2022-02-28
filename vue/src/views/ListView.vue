<template>
	<v-container>
		<v-row v-if="revId && listRevision">
			<v-col md="9" cols="12">
				<h3 class="font-weight-medium">
					{{ $t( 'listrevisioninfo', [
						listRevision.timestamp,
						listRevision.user.username,
						listRevision.comment
					] ) }}
				</h3>
				<template v-if="$can( 'patrol', 'reversion/version' )">
					<h3 class="font-weight-medium">
						<template v-if="!listRevision.patrolled">
							(<a @click="patrol(listRevision.id)">{{ $t( 'markaspatrolled' ) }}</a>)
						</template>
						<template v-else>
							(<span>{{ $t( 'patrolled' ) }}</span>)
						</template>
					</h3>
				</template>
			</v-col>
			<v-col md="3" cols="12">
				<v-btn
					:to="{ name: 'lists-history', params: { id: id } }"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtolisthistory' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<ListInfo
			:list="( revId && listRevision ) ? listRevision.toollist : list"
			:rev-id="revId"
			:show-clipboard-msg="showClipboardMsg"
			@copy-to-clipboard="copyToClipboard"
			@delete-list="deleteList_"
		/>
	</v-container>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';
import ListInfo from '@/components/lists/ListInfo';
import fetchMetaInfo from '@/helpers/metadata';

export default {
	name: 'ListView',
	components: {
		ListInfo
	},
	data() {
		return {
			id: this.$route.params.id,
			revId: this.$route.params.revId,
			showClipboardMsg: false
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'lists-view', this.name );
	},
	computed: {
		...mapState( 'lists', [ 'list', 'listRevision' ] )
	},
	methods: {
		...mapActions( 'lists', [ 'getListById', 'getListRevision', 'deleteList' ] ),
		...mapMutations( 'lists', [ 'LIST', 'LIST_REVISION' ] ),

		formatDate( date ) {
			return this.$moment.utc( date ).format( 'LT ll' );
		},
		patrol( revId ) {
			this.$store.dispatch( 'lists/markRevisionAsPatrolled', {
				id: this.id,
				revId: revId,
				page: 1
			} ).then( () => {
				this.getListInfo();
			} );
		},
		getListInfo() {
			if ( this.revId ) {
				this.getListRevision( { id: this.id, revId: this.revId } );
			} else {
				this.getListById( this.id );
			}
		},
		copyToClipboard() {
			const fullUrl = window.location.origin + this.$route.path;
			this.$copyText( fullUrl ).then( () => {
				this.showClipboardMsg = true;
				setTimeout( () => {
					this.showClipboardMsg = false;
				}, 20000 );
			}, this );
		},
		deleteList_() {
			this.deleteList( this.id ).then(
				() => {
					this.$router.push( { name: 'lists' } );
				}
			);
		}
	},
	mounted() {
		this.getListInfo();
	}
};
</script>
