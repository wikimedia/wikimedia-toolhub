<template>
	<!-- eslint-disable vue/no-mutating-props -- events handled locally -->
	<v-container>
		<v-row>
			<v-col md="6" cols="12">
				<h2 class="text-h4">
					{{ $t( 'tools-edit' ) }}
				</h2>
			</v-col>

			<v-col md="2" cols="12">
				<v-btn
					v-if="value.name"
					:to="{ name: 'tools-view', params: { name: value.name } }"
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
					:disabled="!valid || !$can( 'change', value )"
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
							:rules="[ () => stepIsValid.basic ]"
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
												v-model="value[ id ]"
												:schema="toolSchema.properties[ id ]"
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
							:rules="[ () => stepIsValid.attributes ]"
						>
							{{ $t( 'attributes' ) }}
						</v-stepper-step>
						<v-stepper-content step="2">
							<v-row dense class="my-4">
								<v-col md="12"
									cols="12"
								>
									<v-row>
										<v-col
											v-for="( uischema, id ) in attributesLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="value.annotations[ id ]"
												:schema="annotationsSchema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>
								</v-col>
							</v-row>
						</v-stepper-content>

						<v-stepper-step
							step="3"
							editable
							:rules="[ () => stepIsValid.links ]"
						>
							{{ $t( 'links' ) }}
						</v-stepper-step>
						<v-stepper-content step="3">
							<v-row dense class="my-4">
								<v-col cols="12">
									<v-row class="cols">
										<v-col
											v-for="( uischema, id ) in linksLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="value[ id ]"
												:schema="toolSchema.properties[ id ]"
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
														v-model="value[ id ]"
														:schema="toolSchema.properties[ id ]"
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
							step="4"
							editable
							:rules="[ () => stepIsValid.moreInfo ]"
						>
							{{ $t( 'moreinfo' ) }}
						</v-stepper-step>
						<v-stepper-content step="4">
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
												v-model="value[ id ]"
												:schema="toolSchema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>

									<v-row>
										<v-col
											v-for="( uischema, id ) in annotationsFieldsLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="value.annotations[ id ]"
												:schema="annotationsSchema.properties[ id ]"
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
												v-model="value[ id ]"
												:schema="toolSchema.properties[ id ]"
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
							:disabled="!valid || !$can( 'change', value )"
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
		<CommentDialog v-model="commentDialog" @save="publishChanges" />
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import _ from 'lodash';

import { asTool } from '@/helpers/casl';
import { localizeEnum } from '@/helpers/tools';
import InputWidget from '@/components/common/InputWidget';
import CommentDialog from '@/components/common/CommentDialog';

export default {
	name: 'EditTool',
	components: {
		InputWidget,
		CommentDialog
	},
	props: {
		tool: {
			type: Object,
			required: true
		},
		toolSchema: {
			type: Object,
			required: true
		},
		annotationsSchema: {
			type: Object,
			required: true
		},
		links: {
			type: Array,
			required: true
		}
	},
	data() {
		return {
			step: 1,
			minStep: 1,
			maxStep: 3,
			value: _.cloneDeep( this.tool ),
			initialValue: null,
			commentDialog: false,
			valid: false,
			validityPerField: {}
		};
	},
	computed: {
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
		attributesLayout() {
			const props = this.annotationsSchema.properties;
			return {
				audiences: {
					widget: 'select',
					select: {
						items: () => props.audiences.items.enum.map( ( x ) => {
							return {
								text: localizeEnum( 'audiences', x ),
								value: x
							};
						} )
					},
					multiple: true,
					icon: 'mdi-account-group-outline',
					label: this.$t( 'audiences' )
				},
				content_types: {
					widget: 'select',
					select: {
						items: () => props.content_types.items.enum.map( ( x ) => {
							return {
								text: localizeEnum( 'content_types', x ),
								value: x
							};
						} )
					},
					multiple: true,
					icon: 'mdi-book-open-page-variant-outline',
					label: this.$t( 'contenttypes' )
				},
				tasks: {
					widget: 'select',
					select: {
						items: () => props.tasks.items.enum.map( ( x ) => {
							return {
								text: localizeEnum( 'tasks', x ),
								value: x
							};
						} )
					},
					multiple: true,
					icon: 'mdi-checkbox-multiple-marked-outline',
					label: this.$t( 'tasks' )
				},
				subject_domains: {
					widget: 'select',
					select: {
						items: () => props.subject_domains.items.enum.map( ( x ) => {
							return {
								text: localizeEnum( 'subject_domains', x ),
								value: x
							};
						} )
					},
					multiple: true,
					icon: 'mdi-domain',
					label: this.$t( 'subjectdomains' )
				}
			};
		},
		linksLayout() {
			return {
				api_url: {
					icon: 'mdi-api',
					label: this.$t( 'apiurl' )
				},
				translate_url: {
					icon: 'mdi-translate',
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
			const props = this.toolSchema.properties;
			return {
				tool_type: {
					select: {
						items: () => props.tool_type.enum.map( ( x ) => {
							return {
								text: localizeEnum( 'tool_type', x ),
								value: x
							};
						} )
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
		annotationsFieldsLayout() {
			return {
				wikidata_qid: {
					icon: 'mdi-identifier',
					label: this.$t( 'wikidataqid' )
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
				basic: true,
				attributes: true,
				links: true,
				moreInfo: true
			};

			Object.keys( this.basicInfoLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.basic = false;
				}
			} );

			Object.keys( this.attributesLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.attributes = false;
				}
			} );

			Object.keys( this.linksLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.links = false;
				}
			} );

			Object.keys( this.multiLingualLinksLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.links = false;
				}
			} );

			Object.keys( this.moreInfoLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.moreInfo = false;
				}
			} );

			Object.keys( this.annotationsFieldsLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.moreInfo = false;
				}
			} );

			Object.keys( this.toolStatusLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.moreInfo = false;
				}
			} );

			return valid;
		}
	},
	methods: {
		...mapActions( 'tools', [ 'getSpdxLicenses' ] ),
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
			// if the properties are added the usual way i.e a["key"] = value.
			// This syntax does the same thing except that it also makes
			// the added properties reactive.
			this.$set( this.validityPerField, field, !isValid );
		},
		publishChanges( comment ) {
			const annotations = this.value.annotations;
			const newtool = { ...this.value };

			this.links.forEach( ( field ) => {
				newtool[ field ] = newtool[ field ].filter( ( u ) => {
					return u.url !== undefined &&
						u.url !== null &&
						u.url !== '';
				} );
			} );

			Object.keys( newtool ).forEach( ( field ) => {
				// Overwrite edited toolinfo field with the initial value of
				// field if the field was copied over from annotations
				if (
					_.isEmpty( this.initialValue[ field ] ) &&
					!_.isEmpty( this.initialValue.annotations[ field ] ) &&
					_.isEqual(
						newtool[ field ],
						this.initialValue.annotations[ field ]
					)
				) {
					newtool[ field ] = this.initialValue[ field ];
				}
			} );

			let response = Promise.resolve();

			if ( !_.isEqual( annotations, this.initialValue.annotations ) ) {
				// Update annotations
				response = response.then( () => {
					return this.$store.dispatch( 'tools/editAnnotations', {
						annotations: { ...annotations, comment },
						name: this.value.name
					} );
				} );
			}

			delete newtool.annotations;
			delete this.initialValue.annotations;

			if ( !_.isEqual( newtool, this.initialValue ) ) {
				// Update core tool info
				response = response.then( () => {
					return this.$store.dispatch( 'tools/editTool', {
						info: { ...newtool, comment },
						name: this.value.name
					} );
				} );
			}

			response.then( () => {
				this.$router.push( {
					name: 'tools-view',
					params: { name: this.value.name }
				} ).catch( () => {} );
			} );

			this.commentDialog = false;
		}
	},
	watch: {
		value: {
			handler( newVal ) {
				if ( !this.initialValue && newVal.name ) {
					newVal = JSON.parse( JSON.stringify( newVal ) );
					this.initialValue = newVal;

					const fields = {};

					Object.keys( newVal ).forEach( ( field ) => {
						if (
							_.isEmpty( newVal[ field ] ) &&
							!_.isEmpty( newVal.annotations[ field ] )
						) {
							fields[ field ] = _.cloneDeep(
								newVal.annotations[ field ]
							);
						}
					} );

					this.value = asTool( { ...this.value, ...fields } );
				}
			},
			deep: true,
			immediate: true
		}
	},
	mounted() {
		this.getSpdxLicenses();
	}
};
</script>
