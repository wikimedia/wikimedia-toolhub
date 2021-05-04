<template>
	<v-container v-if="schema">
		<v-row>
			<v-col md="6" cols="12">
				<h2 class="text-h4">
					{{ $t( 'edittool' ) }}
				</h2>
			</v-col>

			<v-col md="2" cols="12">
				<v-btn
					color="accent text--secondary"
					dark
					block
					:to="`/tool/${tool.name}`"
				>
					<v-icon
						dark
						class="me-2"
					>
						mdi-cancel
					</v-icon>
					{{ $t( 'cancel' ) }}
				</v-btn>
			</v-col>

			<v-col md="4" cols="12">
				<v-btn
					color="primary"
					block
					:disabled="!valid"
					@click="showCommentDialog"
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

		<v-form v-model="valid">
			<v-row dense class="my-4">
				<v-col md="7"
					cols="12"
					class="pe-4"
				>
					<v-row class="cols">
						<v-col cols="12" class="text-h5 mt-4">
							{{ $t( 'basicinfo' ) }}
						</v-col>
					</v-row>

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
							/>
						</v-col>
					</v-row>

					<v-row class="cols">
						<v-col cols="12" class="text-h5 mt-4">
							{{ $t( 'links' ) }}
						</v-col>
					</v-row>

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
									/>
								</v-col>
							</v-row>
						</v-col>
					</v-row>
				</v-col>

				<v-col md="5"
					cols="12"
					class="ps-4"
				>
					<div class="text-h5 mt-4">
						{{ $t( 'moreinfo' ) }}
					</div>

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
								v-model="tool[ id ]"
								:schema="schema.properties[ id ]"
								:ui-schema="uischema"
							/>
						</v-col>
					</v-row>
				</v-col>
			</v-row>
		</v-form>

		<v-row>
			<v-col cols="12">
				<ScrollTop />
			</v-col>
		</v-row>

		<v-dialog
			v-model="commentDialog"
			persistent
			max-width="600px"
			@keydown.esc="commentDialog = false"
		>
			<v-card>
				<v-card-title>
					<span class="text-h5">{{ $t( 'editsummary' ) }}</span>
				</v-card-title>

				<v-card-text>
					<v-container>
						<v-row>
							<v-text-field
								ref="comment"
								v-model="comment"
								:label="$t( 'describechanges' )"
								required
								:rules="requiredRule"
								autofocus
								@keydown.enter="publishChanges"
							/>
						</v-row>
					</v-container>
				</v-card-text>

				<v-card-actions>
					<v-spacer />

					<v-btn
						color="accent text--secondary"
						@click="commentDialog = false"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-cancel
						</v-icon>
						{{ $t( 'cancel' ) }}
					</v-btn>

					<v-btn
						color="primary"
						dark
						@click="publishChanges"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-content-save-edit
						</v-icon>
						{{ $t( 'publishchanges' ) }}
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import InputWidget from '@/components/tools/InputWidget';
import ScrollTop from '@/components/tools/ScrollTop';
import fetchMetaInfo from '@/helpers/metadata';

export default {
	name: 'Tool',
	components: {
		InputWidget,
		ScrollTop
	},
	data() {
		return {
			name: this.$route.params.name,
			tool: {
				icon: null,
				title: null,
				description: null,
				author: null,
				repository: null,
				url: null,
				api_url: null,
				translate_url: null,
				bugtracker_url: null,
				user_docs_url: [ { language: this.$i18n.locale, url: null } ],
				developer_docs_url: [ { language: this.$i18n.locale, url: null } ],
				feedback_url: [ { language: this.$i18n.locale, url: null } ],
				privacy_policy_url: [ { language: this.$i18n.locale, url: null } ],
				url_alternates: [ { language: this.$i18n.locale, url: null } ],
				tool_type: null,
				license: null,
				available_ui_languages: [],
				technology_used: [],
				sponsor: [],
				for_wikis: [],
				deprecated: false,
				experimental: false,
				replaced_by: null
			},
			basicInfoLayout: {
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
					icon: 'mdi-account-outline',
					label: this.$t( 'author' )
				},
				repository: {
					icon: 'mdi-source-branch',
					label: this.$t( 'repository' )
				},
				url: {
					icon: 'mdi-link-variant',
					label: this.$t( 'url' )
				}
			},
			linksLayout: {
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
			},
			multiLingualLinksLayout: {
				user_docs_url: {
					items: {
						widget: 'url-multilingual',
						url: {
							icon: 'mdi-file-document-multiple-outline',
							label: this.$t( 'userdocsurl' )
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
					items: {
						widget: 'url-multilingual',
						url: {
							icon: 'mdi-code-tags',
							label: this.$t( 'developerdocsurl' )
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
					items: {
						widget: 'url-multilingual',
						url: {
							icon: 'mdi-comment-processing-outline',
							label: this.$t( 'feedbackurl' )
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
					items: {
						widget: 'url-multilingual',
						url: {
							icon: 'mdi-shield-lock-outline',
							label: this.$t( 'privacypolicyurl' )
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
					items: {
						widget: 'url-multilingual',
						url: {
							icon: 'mdi-link-variant',
							label: this.$t( 'urlalternates' )
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
			},
			moreInfoLayout: {
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
			},
			toolStatusLayout: {
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
			},
			comment: '',
			commentDialog: false,
			requiredRule: [ ( v ) => !!v || this.$t( 'required-field' ) ],
			links: [ 'user_docs_url', 'developer_docs_url', 'privacy_policy_url', 'feedback_url', 'url_alternates' ],
			valid: false
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'edittool', this.name );
	},
	computed: {
		...mapState( 'tools', { toolFromVuex: 'tool' } ),
		...mapState( 'locale', [ 'localeSelect' ] ),
		...mapState( 'tools', [ 'spdxLicenses' ] )
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
		showCommentDialog() {
			this.commentDialog = true;
		},
		publishChanges() {
			const refs = this.$refs,
				comment = refs.comment.value,
				newtool = { ...this.tool };

			if ( !comment ) {
				refs.comment.validate( true );
				return;
			}
			newtool.comment = comment;

			this.links.forEach( ( field ) => {
				newtool[ field ] = newtool[ field ].filter( ( u ) => {
					return u.url !== null && u.url !== '';
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
				this.tool = JSON.parse( JSON.stringify( newVal ) );
				// Inject placeholders in empty link arrays
				for ( const lk in this.links ) {
					const items = this.tool[ this.links[ lk ] ];
					if ( items.length === 0 ) {
						items.push( { url: '', language: this.$i18n.locale } );
					}
				}
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
