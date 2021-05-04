<template>
	<v-container v-if="changes">
		<v-row>
			<v-col md="9" cols="12">
				<h2 class="text-h4">
					{{ $t( 'revisionsdiff' ) }}
				</h2>
			</v-col>

			<v-col md="3" cols="12">
				<v-btn
					:to="`/tool/${name}/history`"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtotoolhistory' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				{{ $t( 'viewrevisionsdiff', [
					name
				] ) }}
			</v-col>
		</v-row>

		<v-row class="my-8">
			<v-col cols="6">
				<h3 class="font-weight-medium">
					{{ $t( 'toolrevisioninfo', [
						formatDate( diffRevision.original.timestamp ),
						diffRevision.original.user.username,
						diffRevision.original.comment
					] ) }}
				</h3>
			</v-col>

			<v-col cols="6">
				<h3 class="font-weight-medium">
					{{ $t( 'toolrevisioninfo', [
						formatDate( diffRevision.result.timestamp ),
						diffRevision.result.user.username,
						diffRevision.result.comment
					] ) }}
				</h3>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="my-4">
				<v-row v-for="(op, idx) in changes"
					:key="idx"
				>
					<v-col cols="6">
						<v-row
							v-if="op.label"
							class="ms-2 cols"
						>
							{{ op.label }}
						</v-row>

						<v-row v-if="op.oldValue !== null"
							class="cols"
						>
							<v-col cols="1">
								<v-icon
									class="mt-3"
									color="secondary"
									small
								>
									mdi-minus
								</v-icon>
							</v-col>

							<v-col cols="11" class="ps-0">
								<v-alert
									border="left"
									colored-border
									color="red lighten-1"
									elevation="2"
									dense
								>
									<template
										v-if="op.index !== null"
									>
										{{ op.index }})
									</template>
									{{ op.oldValue }}
								</v-alert>
							</v-col>
						</v-row>
					</v-col>

					<v-col cols="6">
						<v-row
							v-if="op.label"
							class="ms-2 cols"
						>
							{{ op.label }}
						</v-row>
						<v-row v-if="op.newValue !== null"
							class="cols"
						>
							<v-col cols="1">
								<v-icon
									color="secondary"
									class="mt-3"
									small
								>
									mdi-plus
								</v-icon>
							</v-col>

							<v-col cols="11" class="ps-0">
								<v-alert
									border="left"
									colored-border
									color="green lighten-1"
									elevation="2"
									dense
								>
									<template
										v-if="op.index !== null"
									>
										{{ op.index }})
									</template>
									{{ op.newValue }}
								</v-alert>
							</v-col>
						</v-row>
					</v-col>
				</v-row>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState, mapMutations } from 'vuex';
import fetchMetaInfo from '@/helpers/metadata';

export default {
	name: 'RevisionsDiff',
	data() {
		return {
			name: this.$route.params.name,
			revId: this.$route.params.revId,
			otherRevId: this.$route.params.otherRevId
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'revisionsdiff', this.name );
	},
	computed: {
		...mapState( 'tools', [ 'diffRevision', 'toolRevision' ] ),
		/**
		 * @typedef {Object} ChangeInfo
		 * @property {?string} label - Display label
		 * @property {?number} index - List index position (1-based)
		 * @property {(number|string|boolean|null)} oldValue - Old field value
		 * @property {(number|string|boolean|null)} newValue - New field value
		 */
		/**
		 * Compute changes to render as diff based on JSON Patch from API.
		 *
		 * @return {ChangeInfo[]}
		 */
		changes() {
			if ( !this.diffRevision ) {
				return false;
			}
			const priorRevOps = [ 'remove', 'replace', 'move' ];
			const newRevOps = [ 'add', 'replace', 'move', 'copy' ];
			const normalOps = [];

			// Clone operations with move/copy normalized to remove+add/add
			this.diffRevision.operations.forEach( ( op ) => {
				if ( op.op === 'move' ) {
					normalOps.push( { op: 'remove', path: op.from } );
				}
				if ( op.op === 'copy' || op.op === 'move' ) {
					const value = this.valueForPath( op.from );
					normalOps.push( { op: 'add', path: op.path, value: value } );
				} else {
					normalOps.push( op );
				}
			} );

			let lastProp = null;
			return normalOps.map( ( op ) => {
				const { property, index } = this.parsePath( op.path );
				const change = {
					label: null,
					// Report 1-based indexes in UI
					index: index !== null ? index + 1 : index,
					oldValue: null,
					newValue: null
				};

				// Compute left hand side (old revision change)
				if ( priorRevOps.indexOf( op.op ) !== -1 ) {
					change.oldValue = this.displayFormat(
						property, this.valueForPath( op.path )
					);
				}

				// Compute right hand side (new revision change)
				if ( newRevOps.indexOf( op.op ) !== -1 ) {
					change.newValue = this.displayFormat( property, op.value );
				}

				// Only set label if different from last operation
				// and oldValue or newValue is non-empty.
				if (
					property !== lastProp &&
					(
						change.oldValue !== null ||
						change.newValue !== null
					)
				) {
					change.label = this.propertyLabel( property );
				}
				lastProp = property;
				return change;
			} );
		}
	},
	methods: {
		...mapMutations( 'tools', [ 'DIFF_REVISION' ] ),
		getRevisionsDiff() {
			this.$store.dispatch( 'tools/getRevisionsDiff', {
				name: this.name,
				id: this.revId,
				otherId: this.otherRevId
			} );
		},
		getToolRevision() {
			this.$store.dispatch( 'tools/getToolRevision', {
				name: this.name,
				revId: this.revId
			} );
		},
		/**
		 * Parse a JSON Pointer from a JSON Patch instruction.
		 *
		 * @param {string} path - JSON Pointer (like '/foo/bar/0')
		 * @return {{property: string, index: number|null}}
		 */
		parsePath( path ) {
			const pArr = path.split( '/' );
			return {
				property: pArr[ 1 ],
				index: pArr[ 2 ] ? parseInt( pArr[ 2 ] ) : null
			};
		},
		/**
		 * Compute a localized label for a toolinfo property.
		 *
		 * @param {string} name - Property name (e.g. 'tool_type')
		 * @return {string} Localized label for property
		 */
		propertyLabel( name ) {
			// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
			return this.$i18n.t( name.replace( /_/g, '' ) );
		},
		/**
		 * Normalize "empty" values to null.
		 *
		 * Values considered empty:
		 * - undefined
		 * - null
		 * - '' (empty string)
		 * - {} (empty object)
		 *
		 * @param {*} value
		 * @return {*|null} Normalized value
		 */
		normalizeEmpty( value ) {
			if ( value === '' || value === null || value === undefined ) {
				return null;
			}
			if (
				typeof value === 'object' &&
				value.constructor === Object &&
				Object.keys( value ).length === 0
			) {
				return null;
			}
			return value;
		},
		/**
		 * Find the prior revision value associated with a JSON Pointer.
		 *
		 * @param {string} path - JSON Pointer
		 * @return {*}
		 */
		valueForPath( path ) {
			const { property, index } = this.parsePath( path );
			const value = this.toolRevision &&
				this.toolRevision.toolinfo[ property ];
			if ( Array.isArray( value ) && index !== null ) {
				return value[ index ];
			}
			return value;
		},
		/**
		 * Format a property value for display to the user.
		 *
		 * @param {string} property - Property name
		 * @param {*} value - property value
		 * @return {string|null}
		 */
		displayFormat( property, value ) {
			const linkTypes = [
				'user_docs_url', 'developer_docs_url', 'privacy_policy_url',
				'feedback_url', 'url_alternates'
			];
			if ( linkTypes.indexOf( property ) !== -1 ) {
				if ( !!value && typeof value === 'object' ) {
					value = value.url + ' (' + value.language + ')';
				}
			}
			if ( property.indexOf( 'date' ) !== -1 ) {
				value = this.formatDate( value );
			}
			return this.normalizeEmpty( value );
		},
		formatDate( date ) {
			return this.$moment( date ).format( 'lll' );
		}
	},
	mounted() {
		// Clear any data from a prior view
		this.DIFF_REVISION( null );

		this.getRevisionsDiff();
		this.getToolRevision();
	}
};
</script>
