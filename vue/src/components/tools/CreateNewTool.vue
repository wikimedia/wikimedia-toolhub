<template>
	<v-container v-if="toolsProperties">
		<v-form
			ref="createtoolform"
		>
			<v-col cols="12">
				<v-text-field
					ref="name"
					v-model="name"
					:label="$t( 'name' )"
					required
					:rules="[
						...requiredRule,
						...charsRule( toolsProperties.name.maxLength ),
						...patternRule( toolsProperties.name.pattern )
					]"
					prepend-icon="mdi-identifier"
					:hint="toolsProperties.name.description"
					:counter="toolsProperties.name.maxLength"
				/>
			</v-col>

			<v-col cols="12">
				<v-text-field
					ref="title"
					v-model="title"
					:label="$t( 'title' )"
					required
					:rules="[
						...requiredRule,
						...charsRule( toolsProperties.title.maxLength )
					]"
					prepend-icon="mdi-pencil-outline"
					:hint="toolsProperties.title.description"
					:counter="toolsProperties.title.maxLength"
				/>
			</v-col>

			<v-col cols="12">
				<v-text-field
					ref="description"
					v-model="description"
					:label="$t( 'description' )"
					required
					:rules="[
						...requiredRule,
						...charsRule( toolsProperties.description.maxLength )
					]"
					prepend-icon="mdi-note-text-outline"
					:hint="toolsProperties.description.description"
					:counter="toolsProperties.description.maxLength"
				/>
			</v-col>

			<v-col cols="12">
				<v-text-field
					ref="url"
					v-model="url"
					:label="$t( 'url' )"
					required
					prepend-icon="mdi-link-variant"
					:rules="[
						...requiredRule,
						...urlRule
					]"
					:hint="toolsProperties.url.description"
					:counter="toolsProperties.url.maxLength"
				/>
			</v-col>

			<v-col cols="12">
				<v-text-field
					ref="author"
					v-model="author"
					:label="$t( 'author' )"
					:rules="charsRule( toolsProperties.author.maxLength )"
					prepend-icon="mdi-account-outline"
					:hint="toolsProperties.author.description"
					:counter="toolsProperties.author.maxLength"
				/>
			</v-col>

			<v-col cols="12">
				<v-select
					ref="tool_type"
					v-model="toolTypeSelected"
					:items="toolsProperties.tool_type.enum"
					:label="$t( 'tooltype' )"
					prepend-icon="mdi-toolbox-outline"
					:hint="toolsProperties.tool_type.description"
				/>
			</v-col>

			<v-col cols="12">
				<v-select
					ref="license"
					v-model="licenseSelected"
					:items="spdxLicenses"
					:item-text="item => item.name + ' (' + item.id + ') '"
					:item-value="'id'"
					:label="$t( 'license' )"
					prepend-icon="mdi-license"
					:hint="toolsProperties.license.description"
				/>
			</v-col>

			<v-col cols="12">
				<v-text-field
					ref="repository"
					v-model="repository"
					:label="$t( 'sourcerepository' )"
					prepend-icon="mdi-source-branch"
					:rules="[
						...charsRule( toolsProperties.repository.maxLength ),
						...urlRule
					]"
					:hint="toolsProperties.repository.description"
					:counter="toolsProperties.repository.maxLength"
				/>
			</v-col>

			<v-col cols="">
				<v-text-field
					ref="bugtracker_url"
					v-model="bugtrackerUrl"
					:label="$t( 'bugtrackerurl' )"
					prepend-icon="mdi-bug-outline"
					:rules="[
						...charsRule( toolsProperties.bugtracker_url.maxLength ),
						...urlRule
					]"
					:hint="toolsProperties.bugtracker_url.description"
					:counter="toolsProperties.bugtracker_url.maxLength"
				/>
			</v-col>

			<v-col cols="12">
				<v-row>
					<v-col cols="8">
						<v-text-field
							ref="userDocsUrl"
							v-model="userDocsUrl"
							:label="$t( 'userdocsurl' )"
							prepend-icon="mdi-file-document-multiple-outline"
							:rules="[
								...charsRule( toolsProperties.user_docs_url.items.properties
									.url.maxLength ),
								...urlRule
							]"
							:hint="toolsProperties.user_docs_url.description"
							:counter="toolsProperties.user_docs_url.items.properties
								.url.maxLength"
						/>
					</v-col>

					<v-col cols="4">
						<v-select
							ref="userDocsUrlLang"
							v-model="userDocsUrlLang"
							:items="_localeMap"
							:item-text="item => item.name + ' (' + item.code + ') '"
							:item-value="'code'"
							:label="$t( 'language' )"
							prepend-icon="mdi-web"
						/>
					</v-col>
				</v-row>
			</v-col>

			<v-col cols="12" lg="8">
				<v-btn
					color="primary"
					class="pa-4 mb-4"
					:disabled="$store.state.user.user.is_authenticated === false"
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
import urlRegex from '@/plugins/url-regex';
import patternRegexList from '@/plugins/pattern-regex';

export default {
	name: 'CreateNewTool',
	data() {
		return {
			name: '',
			title: '',
			description: '',
			url: '',
			author: '',
			license: '',
			repository: '',
			userDocsUrl: '',
			userDocsUrlLang: '',
			toolTypeSelected: null,
			licenseSelected: null,
			urlRule: [ ( v ) => !v ? true : urlRegex.test( v ) || this.$t( 'urlinvalid' ) ],
			requiredRule: [ ( v ) => !!v || 'This field is required' ],
			bugtrackerUrl: '',
			docsUrlDefaultLang: 'en'
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
		}
	},
	asyncComputed: {
		toolsProperties: {
			get() {
				return this.getOperationSchema( 'tools_create' ).then(
					( data ) => data.requestBody.content[ 'application/json' ].schema.properties
				);
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getOperationSchema' ] ),
		getSpdxLicenses() {
			this.$store.dispatch( 'tools/getSpdxLicenses' );
		},
		createTool() {
			const refs = this.$refs,
				properties = this.toolProperties,
				toolInfo = {};

			if ( !this.$refs.createtoolform.validate() ) {
				return;
			}

			for ( const tp in properties ) {
				let value;
				if ( properties[ tp ].type === 'string' ) {
					value = '';
				} else if ( properties[ tp ].type === 'array' ) {
					value = [];
				}
				toolInfo[ tp ] = value;
			}

			for ( const ref in refs ) {
				if ( ref !== 'userDocsUrl' &&
                        ref !== 'userDocsUrlLang' ) {
					toolInfo[ ref ] = refs[ ref ].value;
				}
			}

			if ( refs.userDocsUrl.value ) {
				const docsUrlLang = refs.userDocsUrlLang.value;

				toolInfo.user_docs_url = [ {
					language: docsUrlLang || docsUrlDefaultLang,
					url: refs.userDocsUrl.value
				} ];
			}

			toolInfo.comment = this.$t( 'toolcreationcomment', [ refs.title.value ] );
			this.$store.dispatch( 'user/createTool', toolInfo );
		},
		patternRule( exp ) {
			const expRgx = new RegExp( exp );
			let expDesc = '';

			for ( const pr in patternRegexList ) {
				const item = patternRegexList[ pr ];
				const prRgx = new RegExp( item.pattern );

				if ( expRgx.toString() === prRgx.toString() ) {
					expDesc = item.description;
					break;
				}
			}

			return [
				( v ) => !v ? true : expRgx.test( v ) || expDesc
			];
		},
		charsRule( limit ) {
			return [
				( v ) => ( v || '' ).length <= limit || this.$t( 'charslimit', [ limit ] )
			];
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
