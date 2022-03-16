<template>
	<v-container v-if="schema">
		<v-row>
			<v-col md="6" cols="12">
				<h2 class="text-h4">
					{{ $t( 'tools-edit' ) }}
				</h2>
			</v-col>

			<v-col md="2" cols="12">
				<v-btn
					:to="{ name: 'tools-view', params: { name: name } }"
				>
					<v-icon
						left
					>
						mdi-cancel
					</v-icon>
					{{ $t( 'cancel' ) }}
				</v-btn>
			</v-col>

			<v-col md="4" cols="12">
				<v-btn
					color="primary base100--text"
					block
					:disabled="!valid || !$can( 'change', tool )"
					@click="commentDialog = true"
				>
					<v-icon
						dark
						left
					>
						mdi-content-save-edit
					</v-icon>
					{{ $t( 'publishchanges' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-form v-model="valid">
					<v-stepper
						v-model="step"
						non-linear
						vertical
						:elevation="0"
					>
						<v-stepper-step
							step="1"
							editable
							:rules="[ () => stepIsValid.stepOne ]"
						>
							{{ $t( 'basicinfo' ) }}
						</v-stepper-step>
						<v-stepper-content step="1">
							<v-row dense class="my-4">
								<v-col cols="12">
									<v-row class="cols">
										<v-col
											v-for="( uischema, id ) in basicInfoLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="tool[ id ]"
												:schema="schema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>
								</v-col>
							</v-row>
						</v-stepper-content>

						<v-stepper-step
							step="2"
							editable
							:rules="[ () => stepIsValid.stepTwo ]"
						>
							{{ $t( 'links' ) }}
						</v-stepper-step>
						<v-stepper-content step="2">
							<v-row dense class="my-4">
								<v-col cols="12">
									<v-row class="cols">
										<v-col
											v-for="( uischema, id ) in linksLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="tool[ id ]"
												:schema="schema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>

									<v-row>
										<v-col
											v-for="( uischema, id ) in multiLingualLinksLayout"
											:key="id"
											cols="12"
										>
											<v-row>
												<v-col cols="12">
													<InputWidget
														v-model="tool[ id ]"
														:schema="schema.properties[ id ]"
														:ui-schema="uischema"
														@is-valid="storeValidity( $event, id )"
													/>
												</v-col>
											</v-row>
										</v-col>
									</v-row>
								</v-col>
							</v-row>
						</v-stepper-content>

						<v-stepper-step
							step="3"
							editable
							:rules="[ () => stepIsValid.stepThree ]"
						>
							{{ $t( 'moreinfo' ) }}
						</v-stepper-step>
						<v-stepper-content step="3">
							<v-row dense class="my-4">
								<v-col md="12"
									cols="12"
								>
									<v-row>
										<v-col
											v-for="( uischema, id ) in moreInfoLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="tool[ id ]"
												:schema="schema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>

									<div class="text-h5 mt-4">
										{{ $t( 'thistoolis' ) }}
									</div>

									<v-row class="ps-3">
										<v-col
											v-for="( uischema, id ) in toolStatusLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="tool[ id ]"
												:schema="schema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>
								</v-col>
							</v-row>
						</v-stepper-content>
					</v-stepper>
				</v-form>

				<v-row class="justify-space-between mt-4">
					<v-col cols="6">
						<v-btn
							block
							:disabled="step === minStep"
							@click="stepBack"
						>
							<v-icon
								v-if="$vuetify.rtl === false"
								left
							>
								mdi-chevron-left
							</v-icon>
							{{ $t( 'back' ) }}
							<v-icon
								v-if="$vuetify.rtl === true"
								rigth
							>
								mdi-chevron-right
							</v-icon>
						</v-btn>
					</v-col>

					<v-col v-if="step < maxStep"
						cols="6"
					>
						<v-btn
							color="primary base100--text"
							block
							@click="stepContinue"
						>
							<v-icon
								v-if="$vuetify.rtl === true"
								dark
								left
							>
								mdi-chevron-left
							</v-icon>
							{{ $t( 'continue' ) }}
							<v-icon
								v-if="$vuetify.rtl === false"
								dark
								right
							>
								mdi-chevron-right
							</v-icon>
						</v-btn>
					</v-col>
					<v-col v-else
						cols="6"
					>
						<v-btn
							color="primary base100--text"
							block
							:disabled="!valid || !$can( 'change', tool )"
							@click="commentDialog = true"
						>
							<v-icon
								dark
								left
							>
								mdi-content-save-edit
							</v-icon>
							{{ $t( 'publishchanges' ) }}
						</v-btn>
					</v-col>
				</v-row>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<ScrollTop />
			</v-col>
		</v-row>

		<CommentDialog v-model="commentDialog" @save="publishChanges" />
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import InputWidget from '@/components/common/InputWidget';
import ScrollTop from '@/components/common/ScrollTop';
import CommentDialog from '@/components/common/CommentDialog';
import fetchMetaInfo from '@/helpers/metadata';
import { asTool } from '@/helpers/casl';

export default {
	name: 'Tool',
	components: {
		InputWidget,
		ScrollTop,
		CommentDialog
	},
	data() {
		return {
			name: this.$route.params.name,
			step: 1,
			minStep: 1,
			maxStep: 3,
			tool: {
				icon: null,
				title: null,
				description: null,
				author: [],
				repository: null,
				url: null,
				api_url: null,
				translate_url: null,
				bugtracker_url: null,
				user_docs_url: [],
				developer_docs_url: [],
				feedback_url: [],
				privacy_policy_url: [],
				url_alternates: [],
				tool_type: null,
				license: null,
				available_ui_languages: [],
				technology_used: [],
				sponsor: [],
				for_wikis: [],
				experimental: false,
				deprecated: false,
				replaced_by: null
			},
			commentDialog: false,
			links: [ 'user_docs_url', 'developer_docs_url', 'privacy_policy_url', 'feedback_url', 'url_alternates' ],
			valid: false,
			validityPerField: {}
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'tools-edit', this.name );
	},
	computed: {
		...mapState( 'tools', { toolFromVuex: 'tool' } ),
		...mapState( 'locale', [ 'localeSelect' ] ),
		...mapState( 'tools', [ 'spdxLicenses' ] ),
		basicInfoLayout() {
			return {
				icon: {
					icon: 'mdi-tools',
					label: this.$t( 'icon' )
				},
				title: {
					icon: 'mdi-pencil-outline',
					label: this.$t( 'title' ),
					required: true
				},
				description: {
					icon: 'mdi-note-text-outline',
					label: this.$t( 'description' ),
					required: true
				},
				author: {
					widget: 'authors',
					icon: 'mdi-account-multiple-outline',
					appendIcon: 'mdi-plus',
					label: this.$t( 'authors' ),
					items: {
						name: {
							icon: 'mdi-account-outline',
							label: this.$t( 'name' ),
							required: true
						},
						wiki_username: {
							icon: 'mdi-card-account-details-outline',
							label: this.$t( 'wiki-username' )
						},
						developer_username: {
							icon: 'mdi-card-account-details-outline',
							label: this.$t( 'developer-username' )
						},
						email: {
							icon: 'mdi-email-outline',
							label: this.$t( 'email' )
						},
						url: {
							icon: 'mdi-web',
							label: this.$t( 'url' )
						}
					}
				},
				repository: {
					icon: 'mdi-source-branch',
					label: this.$t( 'repository' )
				},
				url: {
					icon: 'mdi-link-variant',
					label: this.$t( 'url' )
				}
			};
		},
		linksLayout() {
			return {
				api_url: {
					icon: 'mdi-bug-outline',
					label: this.$t( 'apiurl' )
				},
				translate_url: {
					icon: 'mdi-bug-outline',
					label: this.$t( 'translateurl' )
				},
				bugtracker_url: {
					icon: 'mdi-bug-outline',
					label: this.$t( 'bugtrackerurl' )
				}
			};
		},
		multiLingualLinksLayout() {
			return {
				user_docs_url: {
					widget: 'url-multilingual',
					icon: 'mdi-file-document-multiple-outline',
					appendIcon: 'mdi-plus',
					label: this.$t( 'userdocsurl' ),
					items: {
						url: {
							icon: 'mdi-file-document-outline',
							label: this.$t( 'url' )
						},
						language: {
							widget: 'select',
							select: {
								items: () => this.localeSelect
							},
							icon: 'mdi-web',
							label: this.$t( 'language' )
						}
					}
				},
				developer_docs_url: {
					widget: 'url-multilingual',
					icon: 'mdi-code-tags',
					appendIcon: 'mdi-plus',
					label: this.$t( 'developerdocsurl' ),
					items: {
						url: {
							icon: 'mdi-code-tags',
							label: this.$t( 'url' )
						},
						language: {
							widget: 'select',
							select: {
								items: () => this.localeSelect
							},
							icon: 'mdi-web',
							label: this.$t( 'language' )
						}
					}
				},
				feedback_url: {
					widget: 'url-multilingual',
					icon: 'mdi-comment-processing-outline',
					appendIcon: 'mdi-plus',
					label: this.$t( 'feedbackurl' ),
					items: {
						url: {
							icon: 'mdi-comment-processing-outline',
							label: this.$t( 'url' )
						},
						language: {
							widget: 'select',
							select: {
								items: () => this.localeSelect
							},
							icon: 'mdi-web',
							label: this.$t( 'language' )
						}
					}
				},
				privacy_policy_url: {
					widget: 'url-multilingual',
					icon: 'mdi-shield-lock-outline',
					appendIcon: 'mdi-plus',
					label: this.$t( 'privacypolicyurl' ),
					items: {
						url: {
							icon: 'mdi-shield-lock-outline',
							label: this.$t( 'url' )
						},
						language: {
							widget: 'select',
							select: {
								items: () => this.localeSelect
							},
							icon: 'mdi-web',
							label: this.$t( 'language' )
						}
					}
				},
				url_alternates: {
					widget: 'url-multilingual',
					icon: 'mdi-link-variant',
					appendIcon: 'mdi-plus',
					label: this.$t( 'urlalternates' ),
					items: {
						url: {
							icon: 'mdi-link-variant',
							label: this.$t( 'url' )
						},
						language: {
							widget: 'select',
							select: {
								items: () => this.localeSelect
							},
							icon: 'mdi-web',
							label: this.$t( 'language' )
						}
					}
				}
			};
		},
		moreInfoLayout() {
			return {
				tool_type: {
					select: {
						items: () => this.schema.properties.tool_type.enum
					},
					icon: 'mdi-toolbox-outline',
					label: this.$t( 'tooltype' )
				},
				license: {
					widget: 'select',
					select: {
						items: () => this.spdxLicenses.map( ( x ) => {
							return {
								text: `${x.name} (${x.id})`,
								value: x.id
							};
						} )
					},
					icon: 'mdi-license',
					label: this.$t( 'license' )
				},
				available_ui_languages: {
					widget: 'select',
					select: {
						items: () => this.localeSelect
					},
					multiple: true,
					icon: 'mdi-tablet-dashboard',
					label: this.$t( 'availableuilanguages' )
				},
				technology_used: {
					widget: 'multi-select',
					icon: 'mdi-cog-outline',
					label: this.$t( 'technologyused' )
				},
				sponsor: {
					widget: 'multi-select',
					icon: 'mdi-account-group-outline',
					label: this.$t( 'sponsor' )
				},
				for_wikis: {
					widget: 'multi-select',
					icon: 'mdi-wikipedia',
					label: this.$t( 'forwikis' )
				}
			};
		},
		toolStatusLayout() {
			return {
				experimental: {
					widget: 'checkbox',
					label: this.$t( 'experimental' )
				},
				deprecated: {
					widget: 'checkbox',
					label: this.$t( 'deprecated' )
				},
				replaced_by: {
					icon: 'mdi-find-replace',
					label: this.$t( 'replacedby' )
				}
			};
		},
		stepIsValid() {
			const valid = {
				stepOne: true,
				stepTwo: true,
				stepThree: true
			};

			Object.keys( this.basicInfoLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepOne = false;
				}
			} );

			Object.keys( this.linksLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepTwo = false;
				}
			} );

			Object.keys( this.multiLingualLinksLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepTwo = false;
				}
			} );

			Object.keys( this.moreInfoLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepThree = false;
				}
			} );

			Object.keys( this.toolStatusLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepThree = false;
				}
			} );

			return valid;
		}
	},
	asyncComputed: {
		schema: {
			get() {
				return this.getRequestSchema( 'tools_update' );
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getRequestSchema' ] ),
		...mapActions( 'tools', [ 'getToolByName', 'getSpdxLicenses' ] ),
		stepBack() {
			this.step = Math.max( this.step - 1, this.minStep );
		},
		stepContinue() {
			this.step = Math.min( this.step + 1, this.maxStep );
		},
		/**
		 * Save the current valid status of a field in a reactive manner.
		 *
		 * @param {boolean} isValid - Is the field valid?
		 * @param {string} field - field name
		 */
		storeValidity( isValid, field ) {
			// validityPerField is dynamically built and therefore not reactive
			// if the properties are added the usual way i.e a["key"] = value
			// this syntax does the same thing except that it also makes
			// the added properties reactive
			this.$set( this.validityPerField, field, !isValid );
		},
		publishChanges( comment ) {
			const newtool = { ...this.tool };
			newtool.comment = comment;

			this.links.forEach( ( field ) => {
				newtool[ field ] = newtool[ field ].filter( ( u ) => {
					return u.url !== undefined && u.url !== null && u.url !== '';
				} );
			} );

			this.$store.dispatch(
				'tools/editTool', { info: newtool, name: this.name }
			);
			this.commentDialog = false;
		}
	},
	watch: {
		toolFromVuex: {
			handler( newVal ) {
				// Deep clone the new state
				this.tool = asTool( JSON.parse( JSON.stringify( newVal ) ) );
			},
			deep: true
		}
	},
	mounted() {
		this.getToolByName( this.name );
		this.getSpdxLicenses();
	}
};
</script>
