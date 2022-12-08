<template>
	<div>
		<v-row v-if="!aggregate">
			<v-col cols="12" class="py-0">
				<v-btn
					class="mb-1 mt-2"
					:to="getDiffRouterObject()"
					:disabled="!( selectedRevisions.length === 2 )"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-compare-horizontal
					</v-icon>
					{{ $t( 'comparetwoselectedrevisions' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<dl v-for="rev in revisions"
			:key="rev.id"
			class="row pa-2"
			:class="{ 'rev-suppressed': rev.suppressed }"
		>
			<dd v-if="!aggregate" class="me-1">
				<v-checkbox
					v-model="checkbox[rev.id]"
					class="ma-0"
					hide-details
					:disabled="!$can( 'view', rev )"
					@change="selectRevision( $event, rev )"
				/>
			</dd>

			<dd v-if="aggregate"
				class="me-1 mt-1"
			>
				<template v-if="rev.content_type === 'tool'">
					<v-icon
						aria-hidden="false"
						:aria-label="$t( 'tool' )"
						role="img"
					>
						mdi-tools
					</v-icon>
				</template>
				<template v-else-if="rev.content_type === 'toollist'">
					<v-icon
						aria-hidden="false"
						:aria-label="$t( 'toollist' )"
						role="img"
					>
						mdi-view-list
					</v-icon>
				</template>
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
					:to="getRevisionRouterObject( rev )"
				>
					{{ rev.timestamp | moment( "utc", "LT ll" ) }}
				</router-link>
				<span v-else>
					{{ rev.timestamp | moment( "utc", "LT ll" ) }}
				</span>
			</dd>

			<dd
				v-if="aggregate"
				class="me-2 mt-1 rev-title"
			>
				<router-link
					:to="getDetailRouterObject( rev )"
				>
					{{ rev.content_title }}
				</router-link>
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

			<dd class="me-1 mt-1 rev-comment" dir="auto">
				<i>({{ rev.comment }})</i>
			</dd>

			<template v-if="$can( 'change', rev )">
				<dd
					v-if="!!rev.parent_id"
					class="me-1 mt-1"
				>
					[<a @click="undoChangesBetweenRevisions( rev )">{{ $t( 'undo' ) }}</a>]
				</dd>

				<dd
					v-if="!!rev.child_id"
					class="me-1 mt-1"
				>
					[<a @click="restoreToRevision( rev )">{{ $t( 'revert' ) }}</a>]
				</dd>
			</template>

			<template v-if="$can( 'change', 'reversion/version' )">
				<dd class="me-1 mt-1">
					<template v-if="rev.suppressed">
						[<a @click="suppress( rev, 'reveal' )">{{ $t( 'reveal' ) }}</a>]
					</template>
					<template v-else-if="!!rev.child_id">
						[<a @click="suppress( rev, 'hide' )">{{ $t( 'hide' ) }}</a>]
					</template>
				</dd>
			</template>

			<template v-if="$can( 'patrol', 'reversion/version' )">
				<dd class="me-1 mt-1">
					<template v-if="!rev.patrolled">
						[<a @click="patrol( rev )">{{ $t( 'markaspatrolled' ) }}</a>]
					</template>
					<template v-else>
						[<span>{{ $t( 'patrolled' ) }}</span>]
					</template>
				</dd>
			</template>
		</dl>
	</div>
</template>

<script>
const TOOL = 'tool';
const LIST = 'toollist';

export default {
	name: 'Revisions',
	props: {
		/**
		 * Array of tool and/or toollist revisions
		 */
		revisions: {
			type: Array,
			required: true
		},
		/**
		 * Revision arrays can be of tool type, toollist type or an aggregate
		 * of both.
		 */
		aggregate: {
			type: Boolean,
			default: false
		}
	},
	data() {
		return {
			selectedRevisions: [],
			selectedRev: {},
			otherSelectedRev: {},
			checkbox: {}
		};
	},
	methods: {
		updateRevisions() {
			this.$emit( 'update-revisions' );
		},
		getRevisionRouterObject( rev ) {
			let routeName;
			if ( rev.content_type === TOOL ) {
				routeName = 'tools-revision';
			} else if ( rev.content_type === LIST ) {
				routeName = 'lists-revision';
			}
			return ( {
				name: routeName,
				params: {
					...this.getUniqueIdentifier( rev ),
					revId: rev.id
				}
			} );
		},
		getDetailRouterObject( rev ) {
			let routeName;
			if ( rev.content_type === TOOL ) {
				routeName = 'tools-view';
			} else if ( rev.content_type === LIST ) {
				routeName = 'lists-view';
			}
			return ( {
				name: routeName,
				params: {
					...this.getUniqueIdentifier( rev )
				}
			} );
		},
		getDiffRouterObject() {
			if ( this.selectedRevisions.length !== 2 ) {
				return {};
			} else {

				const content_type = this.selectedRev.content_type;
				let routeName;

				if ( content_type === TOOL ) {
					routeName = 'tools-diff';
				} else if ( content_type === LIST ) {
					routeName = 'lists-diff';
				}

				return ( {
					name: routeName,
					params: {
						...this.getUniqueIdentifier( this.selectedRev ),
						revId: this.selectedRev.id,
						otherRevId: this.otherSelectedRev.id
					}
				} );
			}
		},
		undoChangesBetweenRevisions( rev ) {
			let vuexMethod;

			if ( rev.content_type === TOOL ) {
				vuexMethod = 'tools/undoChangesBetweenRevisions';
			} else if ( rev.content_type === LIST ) {
				vuexMethod = 'lists/undoChangesBetweenRevisions';
			}

			this.$store.dispatch( vuexMethod, {
				...this.getUniqueIdentifier( rev ),
				revId: rev.id,
				prevRevId: rev.parent_id
			} ).then( this.updateRevisions );

		},
		restoreToRevision( rev ) {
			let vuexMethod;
			if ( rev.content_type === TOOL ) {
				vuexMethod = 'tools/restoreToolToRevision';
			} else if ( rev.content_type === LIST ) {
				vuexMethod = 'lists/restoreListToRevision';
			}

			this.$store.dispatch( vuexMethod, {
				...this.getUniqueIdentifier( rev ),
				revId: rev.id
			} ).then( this.updateRevisions );
		},
		suppress( rev, action ) {
			let vuexMethod;
			if ( rev.content_type === TOOL ) {
				vuexMethod = 'tools/hideRevealRevision';
			} else if ( rev.content_type === LIST ) {
				vuexMethod = 'lists/hideRevealRevision';
			}

			this.$store.dispatch( vuexMethod, {
				...this.getUniqueIdentifier( rev ),
				revId: rev.id,
				action: action
			} ).then( this.updateRevisions );
		},
		patrol( rev ) {
			let vuexMethod;
			if ( rev.content_type === TOOL ) {
				vuexMethod = 'tools/markRevisionAsPatrolled';
			} else if ( rev.content_type === LIST ) {
				vuexMethod = 'lists/markRevisionAsPatrolled';
			}

			this.$store.dispatch( vuexMethod, {
				...this.getUniqueIdentifier( rev ),
				revId: rev.id
			} ).then( this.updateRevisions );
		},
		/**
		 * Selects Two revisions of the same type for comparison.
		 *
		 * @param {Event} event
		 * @param {Object} revSelected
		 */
		selectRevision( event, revSelected ) {
			if ( event ) {
				if ( this.selectedRevisions.length > 1 ) {
					const revToBeRemoved = this.selectedRevisions[ 0 ];
					this.checkbox[ revToBeRemoved.id ] = false;
					this.selectedRevisions.shift();
				}
				this.selectedRevisions.push( revSelected );
			} else {
				this.checkbox[ revSelected.id ] = false;
				const index = this.selectedRevisions.indexOf( revSelected );
				this.selectedRevisions.splice( index, 1 );
			}
			this.selectedRevisions.sort(
				function ( a, b ) { return a.id - b.id; }
			);
			this.selectedRev = this.selectedRevisions[ 0 ] || 0;
			this.otherSelectedRev = this.selectedRevisions[ 1 ] || 0;

		},
		getUniqueIdentifier( rev ) {
			if ( rev.content_type === 'tool' ) {
				return { name: rev.content_id };
			} else if ( rev.content_type === 'toollist' ) {
				return { id: rev.content_id };
			}
		}
	}
};
</script>
