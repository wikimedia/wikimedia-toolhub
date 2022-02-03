<template>
	<v-container v-if="schema">
		<v-form
			ref="createtoolform"
			v-model="valid"
			:disabled="!$can( 'add', 'toolinfo/tool' )"
		>
			<v-col
				v-for="( uischema, id ) in layout"
				:key="id"
				cols="12"
			>
				<InputWidget
					v-model="toolinfo[ id ]"
					:schema="schema.properties[ id ]"
					:ui-schema="uischema"
				/>
			</v-col>
			<v-col cols="12">
				<AgreeTerms />
				<v-btn
					color="primary base100--text"
					class="pa-4 mb-4"
					:disabled="!valid || !$can( 'add', 'toolinfo/tool' )"
					@click="createTool"
				>
					{{ $t( 'createnewtool' ) }}
				</v-btn>
			</v-col>
		</v-form>
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import InputWidget from '@/components/common/InputWidget';
import AgreeTerms from '@/components/common/AgreeTerms';

export default {
	name: 'CreateNewTool',
	components: {
		AgreeTerms,
		InputWidget
	},
	data() {
		return {
			toolinfo: {
				name: null,
				title: null,
				description: null,
				url: null,
				author: [],
				tool_type: null,
				license: null,
				repository: null,
				bugtracker_url: null,
				user_docs_url: [ { language: this.$i18n.locale, url: null } ]
			},
			valid: false
		};
	},
	computed: {
		...mapState( 'user', [ 'toolCreated' ] ),
		...mapState( 'locale', [ 'localeMap' ] ),
		...mapState( 'tools', [ 'spdxLicenses' ] ),

		_localeMap() {
			const localeArr = [];
			Object.keys( this.localeMap ).forEach( ( key ) => {
				localeArr.push( {
					name: this.localeMap[ key ],
					code: key
				} );
			} );

			return localeArr;
		},

		_toolCreated() {
			return this.toolCreated;
		},

		layout() {
			return {
				name: {
					icon: 'mdi-identifier',
					label: this.$t( 'name' ),
					required: true
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
				url: {
					icon: 'mdi-link-variant',
					label: this.$t( 'url' ),
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
				repository: {
					icon: 'mdi-source-branch',
					label: this.$t( 'repository' )
				},
				bugtracker_url: {
					icon: 'mdi-bug-outline',
					label: this.$t( 'bugtrackerurl' )
				},
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
								items: () => this._localeMap.map( ( x ) => {
									return {
										text: `${x.name} (${x.code})`,
										value: x.code
									};
								} )
							},
							icon: 'mdi-web',
							label: this.$t( 'language' )
						}
					}
				}
			};
		}
	},
	asyncComputed: {
		schema: {
			get() {
				return this.getRequestSchema( 'tools_create' );
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getRequestSchema' ] ),
		getSpdxLicenses() {
			this.$store.dispatch( 'tools/getSpdxLicenses' );
		},
		createTool() {
			const newtool = { ...this.toolinfo };
			newtool.user_docs_url = newtool.user_docs_url.filter( ( u ) => {
				return u.url !== null && u.url !== '';
			} );
			newtool.comment = this.$t(
				'toolcreationcomment', [ newtool.title ]
			);
			this.$store.dispatch( 'tools/createTool', newtool );
		}
	},
	watch: {
		_toolCreated() {
			this.$refs.createtoolform.reset();
		}
	},
	mounted() {
		this.getSpdxLicenses();
	}
};
</script>
