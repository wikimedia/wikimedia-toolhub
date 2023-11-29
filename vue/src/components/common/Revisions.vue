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
			<dd v-if="aggregate" class="me-1 mt-1">
				<template v-if="getDiffRouterObject( rev )">
					(<router-link :to="getDiffRouterObject( rev )">
						<span>{{ $t( 'diff' ) }}</span>
					</router-link>
				</template>
				<template v-else>
					({{ $t( 'diff' ) }}
				</template>
				{{ $t( 'pipe-separator' ) }}
				<router-link
					:to="getRouterObject( rev, 'history' )">
					<span>{{ $t( 'hist' ) }}</span>
				</router-link>)
			</dd>

			<dd v-else class="me-2 mt-1 rev-timestamp">
				<router-link
					v-if="$can( 'view', rev )"
					:to="getRouterObject( rev, 'revision' )"
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
					:to="getRouterObject( rev, 'view' )"
				>
					{{ rev.content_title }}
				</router-link>
			</dd>

			<template v-if="$can( 'view', rev )">
				<dd class="me-1 mt-1 rev-user">
					<a
						:href="`https://meta.wikimedia.org/wiki/User:${rev.user.username}`"
						target="_blank"
					>{{ rev.user.username }}</a>
				</dd>
				<dd class="me-1 mt-1 rev-user-talk">
					(<a
						:href="`https://meta.wikimedia.org/wiki/User_talk:${rev.user.username}`"
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
					[<a @click="performRevisionAction(
						rev,
						'undo',
						{ prevRevId: rev.parent_id } )"
					>{{ $t( 'undo' ) }}</a>]
				</dd>

				<dd
					v-if="!!rev.child_id"
					class="me-1 mt-1"
				>
					[<a @click="performRevisionAction( rev, 'restore' );
					">{{ $t( 'revert' ) }}</a>]
				</dd>
			</template>

			<template v-if="$can( 'change', 'reversion/version' )">
				<dd class="me-1 mt-1">
					<template v-if="rev.suppressed">
						[<a @click="performRevisionAction( rev, 'suppress', { action: 'reveal' } );"
						>{{ $t( 'reveal' ) }}</a>]
					</template>
					<template v-else-if="!!rev.child_id">
						[<a @click="performRevisionAction( rev, 'suppress', { action: 'hide' } )"
						>{{ $t( 'hide' ) }}</a>]
					</template>
				</dd>
			</template>

			<template v-if="$can( 'patrol', 'reversion/version' )">
				<dd class="me-1 mt-1">
					<template v-if="!rev.patrolled">
						[<a @click="performRevisionAction( rev, 'patrol' )"
						>{{ $t( 'markaspatrolled' ) }}</a>]
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
		getRouterObject( rev, routeType ) {
			let routeName;
			const baseRoute = rev.content_type === 'tool' ? 'tools' : 'lists';
			const params = { ...this.getUniqueIdentifier( rev ) };

			switch ( routeType ) {
				case 'revision':
					routeName = `${baseRoute}-revision`;
					params.revId = rev.id;
					break;
				case 'history':
					routeName = `${baseRoute}-history`;
					params.revId = rev.id;
					break;
				case 'view':
					routeName = `${baseRoute}-view`;
					break;
				default:
					return {};
			}

			return {
				name: routeName,
				params: params
			};
		},
		getDiffRouterObject( rev = null ) {
			if ( !this.aggregate && this.selectedRevisions.length !== 2 ) {
				return {};
			}
			let revId, otherRevId;

			if ( !rev ) {
				rev = this.selectedRev;
				revId = this.selectedRev.id;
				otherRevId = this.otherSelectedRev.id;
			} else {
				if ( !rev.parent_id ) {
					return null;
				}
				revId = rev.parent_id;
				otherRevId = rev.id;
			}

			const routeName = rev.content_type === 'tool' ? 'tools-diff' : 'lists-diff';

			return {
				name: routeName,
				params: {
					...this.getUniqueIdentifier( rev ),
					revId,
					otherRevId
				}
			};
		},
		performRevisionAction( rev, actionType, additionalParams = {} ) {
			const vuexMethodMap = {
				undo: {
					[ TOOL ]: 'tools/undoChangesBetweenRevisions',
					[ LIST ]: 'lists/undoChangesBetweenRevisions'
				},
				restore: {
					[ TOOL ]: 'tools/restoreToolToRevision',
					[ LIST ]: 'lists/restoreListToRevision'
				},
				suppress: {
					[ TOOL ]: 'tools/hideRevealRevision',
					[ LIST ]: 'lists/hideRevealRevision'
				},
				patrol: {
					[ TOOL ]: 'tools/markRevisionAsPatrolled',
					[ LIST ]: 'lists/markRevisionAsPatrolled'
				}
			};

			const vuexMethod = vuexMethodMap[ actionType ][ rev.content_type ];
			const params = {
				...this.getUniqueIdentifier( rev ),
				revId: rev.id,
				...additionalParams
			};

			this.$store.dispatch( vuexMethod, params ).then( this.updateRevisions );
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
			if ( rev.content_type === TOOL ) {
				return { name: rev.content_id };
			} else if ( rev.content_type === LIST ) {
				return { id: rev.content_id };
			}
		}
	}
};
</script>
