<template>
	<v-container>
		<v-row>
			<v-col md="9" cols="12">
				<h2 class="text-h4">
					{{ $t( 'lists-history' ) }}
				</h2>
			</v-col>

			<v-col md="3" cols="12">
				<v-btn
					:to="{ name: 'lists-view', params: { id: id } }"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtolistinfo' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'listhistory-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<v-btn
					:to="{
						name: 'lists-diff',
						params: {
							id: id,
							revId: selectedId,
							otherRevId: otherSelectedId
						}
					}"
					:disabled="!( selectedId && otherSelectedId)"
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
				<dl v-for="rev in listRevisions"
					:key="rev.id"
					class="row pa-2"
					:class="{ 'rev-suppressed': rev.suppressed }"
				>
					<dd class="me-1">
						<v-checkbox
							ref="rev.id"
							v-model="checkbox[rev.id]"
							class="ma-0"
							hide-details
							:disabled="!$can( 'view', rev )"
							@change="selectListRevision($event, rev.id)"
						/>
					</dd>

					<template v-if="$can( 'patrol', 'reversion/version' )">
						<dd class="me-1 mt-1">
							<template v-if="!rev.patrolled">
								<v-icon class="error--text"
									aria-hidden="false"
									:aria-label="$t( 'unpatrolled' )"
									role="img"
								>
									mdi-exclamation-thick
								</v-icon>
							</template>
							<template v-else>
								<v-icon class="success--text"
									aria-hidden="false"
									:aria-label="$t( 'patrolled' )"
									role="img"
								>
									mdi-check-bold
								</v-icon>
							</template>
						</dd>
					</template>

					<dd class="me-2 mt-1 rev-timestamp">
						<router-link
							v-if="$can( 'view', rev )"
							:to="{
								name: 'lists-revision',
								params: {
									id: id,
									revId: rev.id
								}
							}"
						>
							{{ rev.timestamp | moment( "utc", "LT ll" ) }}
						</router-link>
						<span v-else>
							{{ rev.timestamp | moment( "utc", "LT ll" ) }}
						</span>
					</dd>

					<template v-if="$can( 'view', rev )">
						<dd class="me-1 mt-1 rev-user">
							<a
								:href="`http://meta.wikimedia.org/wiki/User:${rev.user.username}`"
								target="_blank"
							>{{ rev.user.username }}</a>
						</dd>

						<dd class="me-1 mt-1 rev-user-talk">
							(<a
								:href="`http://meta.wikimedia.org/wiki/User_talk:${rev.user.username}`"
								target="_blank"
							>{{ $t( 'talk' ) }}</a>)
						</dd>
					</template>
					<template v-else>
						<dd class="me-1 mt-1 rev-user">
							{{ rev.user.username }}
						</dd>
						<dd class="me-1 mt-1 rev-user-talk" />
					</template>

					<dd class="me-1 mt-1 rev-comment">
						<i>({{ rev.comment }})</i>
					</dd>

					<template v-if="$can( 'view', rev )">
						<dd class="me-1 mt-1">
							(<a @click="undoChangesBetweenRevisions(rev.id)">{{ $t( 'undo' ) }}</a>)
						</dd>

						<dd class="me-1 mt-1">
							(<a @click="restoreListToRevision(rev.id)">{{ $t( 'revert' ) }}</a>)
						</dd>
					</template>

					<template v-if="$can( 'change', 'reversion/version' )">
						<dd class="me-1 mt-1">
							<template v-if="rev.suppressed">
								(<a @click="suppress(rev.id, 'reveal')">{{ $t( 'reveal' ) }}</a>)
							</template>
							<template v-else>
								(<a @click="suppress(rev.id, 'hide')">{{ $t( 'hide' ) }}</a>)
							</template>
						</dd>
					</template>

					<template v-if="$can( 'patrol', 'reversion/version' )">
						<dd class="me-1 mt-1">
							<template v-if="!rev.patrolled">
								(<a @click="patrol(rev.id)">{{ $t( 'markaspatrolled' ) }}</a>)
							</template>
							<template v-else>
								(<span>{{ $t( 'patrolled' ) }}</span>)
							</template>
						</dd>
					</template>
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
	name: 'ListHistory',
	data() {
		return {
			id: this.$route.params.id,
			page: 1,
			itemsPerPage: 10,
			selectedRevisions: [],
			selectedId: 0,
			otherSelectedId: 0,
			checkbox: {}
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'lists-history', String( this.id ) );
	},
	computed: {
		...mapState( 'lists', [ 'listRevisions', 'numRevisions' ] )
	},
	methods: {
		getRevisions() {
			this.$store.dispatch( 'lists/updateListRevisions', { page: this.page, id: this.id } );
		},
		goToPage( page ) {
			this.page = page;
			this.getRevisions();
		},
		undoChangesBetweenRevisions( revId ) {
			this.$store.dispatch( 'lists/undoChangesBetweenRevisions', {
				id: this.id,
				revId: revId,
				page: this.page
			} );
		},
		restoreListToRevision( revId ) {
			this.$store.dispatch( 'lists/restoreListToRevision', {
				id: this.id,
				revId: revId,
				page: this.page
			} );
		},
		suppress( revId, action ) {
			this.$store.dispatch( 'lists/hideRevealRevision', {
				id: this.id,
				revId: revId,
				page: this.page,
				action: action
			} );
		},
		patrol( revId ) {
			this.$store.dispatch( 'lists/markRevisionAsPatrolled', {
				id: this.id,
				revId: revId,
				page: this.page
			} );
		},
		selectListRevision( event, idSelected ) {
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

			this.selectedId = this.selectedRevisions[ 0 ] || 0;
			this.otherSelectedId = this.selectedRevisions[ 1 ] || 0;
		}
	},
	mounted() {
		this.getRevisions();
	}
};
</script>
