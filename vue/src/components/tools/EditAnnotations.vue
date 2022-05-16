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
					:disabled="!valid || $can( 'change', value )"
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
							{{ $t( 'links' ) }}
						</v-stepper-step>
						<v-stepper-content step="1">
							<v-row dense class="my-4">
								<v-col md="12" cols="12">
									<v-row class="cols">
										<v-col
											v-for="( uischema, id ) in linksLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="value.annotations[ id ]"
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
														v-model="value.annotations[ id ]"
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
							step="2"
							editable
							:rules="[ () => stepIsValid.stepTwo ]"
						>
							{{ $t( 'moreinfo' ) }}
						</v-stepper-step>
						<v-stepper-content step="2">
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
												v-model="value.annotations[ id ]"
												:schema="schema.properties[ id ]"
												:ui-schema="uischema"
												@is-valid="storeValidity( $event, id )"
											/>
										</v-col>
									</v-row>
									<div class="text-h5 mt-4">
										{{ $t( 'thistoolis' ) }}
									</div>
									<v-row>
										<v-col
											v-for="( uischema, id ) in toolStatusLayout"
											:key="id"
											cols="12"
										>
											<InputWidget
												v-model="value.annotations[ id ]"
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
							color="primary base100--text"
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
							:disabled="!valid || $can( 'change', value )"
							@click="commentDialog = true"
						>
							<v-icon
								dark
								class="me-2"
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
import { mapState } from 'vuex';
import _ from 'lodash';
import InputWidget from '@/components/common/InputWidget';
import CommentDialog from '@/components/common/CommentDialog';

export default {
	name: 'EditAnnotations',
	components: {
		InputWidget,
		CommentDialog
	},
	props: {
		value: {
			type: Object,
			required: true
		},
		schema: {
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
			maxStep: 2,
			initialValue: null,
			commentDialog: false,
			valid: false,
			validityPerField: {}
		};
	},
	computed: {
		...mapState( 'locale', [ 'localeSelect' ] ),
		linksLayout() {
			return {
				api_url: {
					icon: 'mdi-bug-outline',
					label: this.$t( 'apiurl' )
				},
				repository: {
					icon: 'mdi-source-branch',
					label: this.$t( 'repository' )
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
				}
			};
		},
		moreInfoLayout() {
			return {
				icon: {
					icon: 'mdi-tools',
					label: this.$t( 'icon' )
				},
				tool_type: {
					select: {
						items: () => this.schema.properties.tool_type.enum
					},
					icon: 'mdi-toolbox-outline',
					label: this.$t( 'tooltype' )
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
				for_wikis: {
					widget: 'multi-select',
					icon: 'mdi-wikipedia',
					label: this.$t( 'forwikis' )
				},
				wikidata_qid: {
					icon: 'mdi-identifier',
					label: this.$t( 'wikidataqid' )
				}

			};
		},
		toolStatusLayout() {
			return {
				deprecated: {
					widget: 'checkbox',
					label: this.$t( 'deprecated' )
				},
				experimental: {
					widget: 'checkbox',
					label: this.$t( 'experimental' )
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
				stepTwo: true
			};
			Object.keys( this.linksLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepOne = false;
				}
			} );
			Object.keys( this.multiLingualLinksLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepOne = false;
				}
			} );
			Object.keys( this.moreInfoLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepTwo = false;
				}
			} );
			Object.keys( this.toolStatusLayout ).forEach( ( field ) => {
				if ( this.validityPerField[ field ] === false ) {
					valid.stepTwo = false;
				}
			} );
			return valid;
		}
	},
	methods: {
		stepBack() {
			this.step = Math.max( this.step - 1, this.minStep );
		},
		stepContinue() {
			this.step = Math.min( this.step + 1, this.maxStep );
		},
		storeValidity( bool, field ) {
			// validityPerField is dynamically built and therefore not reactive
			// if the properties are added the usual way i.e a["key"] = value
			// this syntax does the same thing except that it also makes
			// the added properties reactive
			this.$set( this.validityPerField, field, !bool );
		},
		publishChanges( comment ) {
			const annotations = { ...this.value.annotations };

			const annotations_changed = !_.isEqual(
				annotations,
				this.initialValue.annotations );

			annotations.comment = comment;

			this.links.forEach( ( field ) => {
				if ( annotations[ field ] ) {
					annotations[ field ] = annotations[ field ].filter( ( u ) => {
						return u.url !== undefined && u.url !== null && u.url !== '';
					} );
				}
			} );

			// set response to resolved promise so we can always
			// chain it with .then whether annotations_changed is true or false
			let response = Promise.resolve();

			if ( annotations_changed ) {
				response = this.$store.dispatch(
					'tools/editAnnotations', { annotations, name: this.value.name }
				);
			}

			response.then( () => {
				this.$router.push(
					{
						name: 'tools-view',
						params: { name: this.value.name }
					}
				).catch( () => {} );
			} );

			this.commentDialog = false;
		}
	},
	watch: {
		value: {
			handler( newVal ) {
				if ( !this.initialValue && newVal.name ) {
					this.initialValue = JSON.parse( JSON.stringify( newVal ) );
				}
			},
			deep: true,
			immediate: true
		}
	}
};
</script>
