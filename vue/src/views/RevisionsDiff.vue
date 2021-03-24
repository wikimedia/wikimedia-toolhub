<template>
	<v-container v-if="diffRevision">
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
				<v-row v-for="(op, i) in diffRevision.operations"
					:key="i"
				>
					<v-col cols="6">
						<v-row class="ms-2 cols">
							{{ renderPropertyName( op.path) }}
						</v-row>

						<v-row v-if="op.op === 'remove'
								|| op.op === 'replace'
								|| op.op === 'move'"
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
									v-if="getPropertyValueForRevision('previous', op.path)"
									border="left"
									colored-border
									color="red lighten-1"
									elevation="2"
									dense
								>
									<template
										v-if="getProperty(op.path).index !== ''"
									>
										{{ getProperty(op.path).index + 1 }})
									</template>
									{{ getPropertyValueForRevision('previous', op.path) }}
								</v-alert>
							</v-col>
						</v-row>
					</v-col>

					<v-col cols="6">
						<v-row class="ms-2 cols">
							{{ renderPropertyName( op.path ) }}
						</v-row>
						<v-row v-if="op.op === 'add' ||
								op.op === 'replace' ||
								op.op === 'move' ||
								op.op === 'copy'"
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
									v-if="op.value"
									border="left"
									colored-border
									color="green lighten-1"
									elevation="2"
									dense
								>
									<template
										v-if="getProperty(op.path).index !== ''"
									>
										{{ getProperty(op.path).index + 1 }})
									</template>
									{{ getPropertyValueForRevision( 'next', op.path ) }}
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

export default {
	name: 'RevisionsDiff',
	data() {
		return {
			name: this.$route.params.name,
			revId: this.$route.params.revId,
			otherRevId: this.$route.params.otherRevId,
			propertiesModified: [],
			diffRevision: null,
			toolRevision: null
		};
	},
	computed: {
		...mapState( 'tools', {
			diffRevisionFromVuex: 'diffRevision',
			toolRevisionFromVuex: 'toolRevision'
		} )
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
		getProperty( path ) {
			const pArr = path.split( '/' );
			return {
				property: pArr[ 1 ],
				index: pArr[ 2 ] ? parseInt( pArr[ 2 ] ) : ''
			};
		},
		renderPropertyName( path ) {
			const propertyName = this.getProperty( path ).property;
			// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
			return this.$i18n.t( propertyName.replace( /_/g, '' ) );
		},
		getPropertyValueForRevision( type, path ) {
			const extract = this.getProperty( path ),
				property = extract.property,
				index = extract.index,
				links = [ 'user_docs_url', 'developer_docs_url', 'privacy_policy_url',
					'feedback_url', 'url_alternates' ];
			let propertyValue = '';

			if ( type === 'previous' ) {
				propertyValue = this.toolRevision && this.toolRevision.toolinfo[ property ];
				if ( Array.isArray( propertyValue ) ) {
					propertyValue = this.toolRevision &&
						this.toolRevision.toolinfo[ property ][ index ];
				}
			} else {
				const diffOperations = this.diffRevision && this.diffRevision.operations;
				diffOperations.forEach( ( op ) => {
					if ( op.path === path ) {
						propertyValue = op.value;
					}
				} );
			}

			if ( links.indexOf( property ) !== -1 ) {
				if ( !!propertyValue && typeof propertyValue === 'object'
				) {
					propertyValue = propertyValue.url + ' (' + propertyValue.language + ')';
				}
			}

			if ( path.indexOf( 'date' ) !== -1 ) {
				propertyValue = this.formatDate( propertyValue );
			}

			return propertyValue;
		},
		formatDate( date ) {
			return this.$moment( date ).format( 'lll' );
		}
	},
	watch: {
		toolRevisionFromVuex: {
			handler( newVal ) {
				this.toolRevision = JSON.parse( JSON.stringify( newVal ) );
			},
			deep: true
		},
		diffRevisionFromVuex: {
			handler( newVal ) {
				// Deep clone the new state
				this.diffRevision = JSON.parse( JSON.stringify( newVal ) );

				// Modify the 'copy' and 'move' operations
				const diffOperations = this.diffRevision && this.diffRevision.operations;

				for ( const opIndex in diffOperations ) {
					const op = diffOperations[ opIndex ];

					if ( op.op === 'move' ) {
						diffOperations.push( {
							op: 'remove',
							path: op.from
						} );
					}

					if ( op.op === 'copy' || op.op === 'move' ) {
						const value = this.getPropertyValueForRevision( 'previous', op.from );
						diffOperations.push( {
							op: 'add',
							path: op.path,
							value: value
						} );
						diffOperations.splice( opIndex, 1 );
					}
				}
			},
			deep: true
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
