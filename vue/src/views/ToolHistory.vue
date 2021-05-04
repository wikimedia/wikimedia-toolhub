<template>
	<v-container>
		<v-row>
			<v-col md="9" cols="12">
				<h2 class="text-h4">
					{{ $t( 'toolhistory' ) }}
				</h2>
			</v-col>

			<v-col md="3" cols="12">
				<v-btn
					:to="`/tool/${name}`"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtotoolinfo' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'toolhistory-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<v-btn
					:to="`/tool/${name}/history/revision/${selectedId}/diff/${otherSelectedId}`"
					:disabled="!selectedId || !otherSelectedId"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-compare-horizontal
					</v-icon>
					{{ $t( 'comparetwoselectedrevisions' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="my-4">
				<dl v-for="rev in toolRevisions"
					:key="rev.id"
					class="row pa-2"
				>
					<dd class="me-1">
						<v-checkbox
							ref="rev.id"
							v-model="checkbox[rev.id]"
							class="ma-0"
							hide-details
							@change="selectToolRevision($event, rev.id)"
						/>
					</dd>

					<dd class="me-2 mt-1">
						<router-link :to="`/tool/${name}/history/revision/${rev.id}`">
							{{ rev.timestamp | moment( "LT ll" ) }}
						</router-link>
					</dd>

					<dd class="me-1 mt-1">
						<a :href="`http://meta.wikimedia.org/wiki/User:${rev.user.username}`" target="_blank">{{ rev.user.username
						}}</a>
					</dd>

					<dd class="me-1 mt-1">
						(<a :href="`http://meta.wikimedia.org/wiki/User_talk:${rev.user.username}`"
							target="_blank"
						>{{ $t( 'talk' ) }}</a>)
					</dd>

					<dd class="me-1 mt-1">
						<i>({{ rev.comment }})</i>
					</dd>

					<dd class="me-1 mt-1">
						(<a @click="undoChangesBetweenRevisions(rev.id)">{{ $t( 'undo' ) }}</a>)
					</dd>

					<dd class="me-1 mt-1">
						(<a @click="restoreToolToRevision(rev.id)">{{ $t( 'revert' ) }}</a>)
					</dd>
				</dl>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-pagination
					v-if="numRevisions > 0"
					v-model="page"
					:length="Math.ceil( numRevisions / itemsPerPage )"
					class="ma-4"
					total-visible="5"
					@input="goToPage"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import fetchMetaInfo from '@/helpers/metadata';

export default {
	name: 'ToolHistory',
	data() {
		return {
			name: this.$route.params.name,
			page: 1,
			itemsPerPage: 10,
			selectedRevisions: [],
			selectedId: '',
			otherSelectedId: '',
			checkbox: {}
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'toolhistory', this.name );
	},
	computed: {
		...mapState( 'tools', [ 'toolRevisions', 'numRevisions' ] )
	},
	methods: {
		getRevisions() {
			this.$store.dispatch( 'tools/updateToolRevisions', { page: this.page, name: this.name } );
		},
		goToPage( page ) {
			this.page = page;
			this.getRevisions();
		},
		undoChangesBetweenRevisions( id ) {
			this.$store.dispatch( 'tools/undoChangesBetweenRevisions', {
				name: this.name,
				id: id,
				page: this.page
			} );
		},
		restoreToolToRevision( id ) {
			this.$store.dispatch( 'tools/restoreToolToRevision', {
				name: this.name,
				id: id,
				page: this.page
			} );
		},
		selectToolRevision( event, idSelected ) {
			if ( event ) {
				if ( this.selectedRevisions.length > 1 ) {
					const idToBeRemoved = this.selectedRevisions[ 0 ];
					this.checkbox[ idToBeRemoved ] = false;
					this.selectedRevisions.shift();
				}
				this.selectedRevisions.push( idSelected );
			} else {
				this.checkbox[ idSelected ] = false;
				const index = this.selectedRevisions.indexOf( idSelected );
				this.selectedRevisions.splice( index, 1 );
			}

			this.selectedRevisions.sort(
				function ( a, b ) { return a - b; }
			);

			this.selectedId = this.selectedRevisions[ 0 ];
			this.otherSelectedId = this.selectedRevisions[ 1 ];
		}
	},
	mounted() {
		this.getRevisions();
	}
};
</script>
