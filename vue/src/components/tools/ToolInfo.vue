<template>
	<v-container v-if="tool">
		<v-app-bar
			v-if="!revId"
			color="base100"
			flat
			height="auto"
			class="tool-app-bar"
			:class="{ 'tool-app-bar-xs': $vuetify.breakpoint.xs }"
		>
			<ToolEditButton :tool="tool" />
			<FavoriteButton :tool="tool" />
			<v-btn
				:to="{ name: 'tools-history', params: { name: tool.name } }"
				:small="$vuetify.breakpoint.smAndDown"
				class="my-1 mx-2"
			>
				<v-icon class="me-2">
					mdi-history
				</v-icon>
				{{ $t( 'viewhistory' ) }}
			</v-btn>
			<ToolMenu :tool="tool" :smallicon="false" />
		</v-app-bar>

		<v-row
			class="mt-4"
			no-gutters
		>
			<v-col cols="12">
				<dl class="d-flex align-center flex-nowrap">
					<dt class="me-4">
						<ToolImage :tool="tool" />
					</dt>
					<dd>
						<h2 class="text-h3">
							{{ tool.title }}
							<div
								v-if="tool.subtitle"
								class="text-subtitle-1"
							>
								{{ tool.subtitle }}
							</div>
						</h2>
					</dd>
				</dl>
				<div class="mt-4" dir="auto">
					{{ tool.description }}
				</div>
				<dl class="tool-info__authors row mx-0 mt-4 text-subtitle-1">
					<dt class="me-2 my-1">{{ $t( 'authors' ) }}:</dt>
					<dd
						v-for="( author, index ) in tool.author"
						:key="author.name + index"
						class="me-2"
					>
						<AuthorDetails :author="author" />
					</dd>
				</dl>
				<div>
					<v-btn
						class="mt-4 me-3"
						color="primary base100--text"
						dark
						:href="`${tool.url}`"
						target="_blank"
						:small="$vuetify.breakpoint.smAndDown"
					>
						{{ $t( 'browsetool' ) }}
						<v-icon
							dark
							right
						>
							mdi-link-variant
						</v-icon>
					</v-btn>
					<v-btn
						v-if="getDisplayedScalar( 'repository' )"
						outlined
						color="primary base100--text"
						class="mt-4"
						:href="getDisplayedScalar( 'repository' )"
						target="_blank"
						:small="$vuetify.breakpoint.smAndDown"
					>
						{{ $t( 'sourcecode' ) }}
						<v-icon
							dark
							right
						>
							mdi-code-json
						</v-icon>
					</v-btn>
				</div>

				<v-alert
					v-if="getDisplayedScalar( 'experimental' ) ||
						getDisplayedScalar( 'deprecated' )"
					border="left"
					type="error"
					elevation="2"
					width="100%"
					class="mt-4"
				>
					<template v-if="getDisplayedScalar( 'experimental' )">
						{{ $t( 'tool-experimental-error' ) }}
					</template>

					<template v-if="getDisplayedScalar( 'deprecated' )">
						{{ $t( 'tool-deprecated-error' ) }}
					</template>
				</v-alert>
				<v-alert
					v-if="getDisplayedScalar( 'replaced_by' )"
					border="left"
					color="primary base100--text"
					dark
					elevation="2"
					type="info"
					width="100%"
					class="mt-4"
				>
					{{ $t( 'tool-replacement-link',
						[ getDisplayedScalar( 'replaced_by' ) ] ) }}
				</v-alert>
			</v-col>
		</v-row>
		<v-row>
			<v-col
				v-if="attributesSection.length"
				md="6"
				cols="12"
			>
				<h3 class="text-h5 mt-4">
					{{ $t( 'attributes' ) }}
				</h3>
				<ToolInfoSection :section="attributesSection" />
			</v-col>
			<v-col
				v-if="usageSection.length"
				md="6"
				cols="12"
			>
				<h3 class="text-h5 mt-4">
					{{ $t( 'usage' ) }}
				</h3>
				<ToolInfoSection :section="usageSection" />
			</v-col>
		</v-row>
		<v-row>
			<v-col
				v-if="contributingSection.length"
				md="6"
				cols="12"
			>
				<h3 class="text-h5 mt-4">
					{{ $t( 'contributing' ) }}
				</h3>
				<ToolInfoSection :section="contributingSection" />
			</v-col>
			<v-col
				v-if="moreInfoSection.length"
				md="6"
				cols="12"
			>
				<h3 class="text-h5 mt-4">
					{{ $t( 'moreinfo' ) }}
				</h3>
				<ToolInfoSection :section="moreInfoSection" />
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<ScrollTop />
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import _ from 'lodash';

import { ensureArray } from '@/helpers/array';
import { forWikiLabel, localizeEnum } from '@/helpers/tools';

import AuthorDetails from '@/components/tools/AuthorDetails';
import FavoriteButton from '@/components/tools/FavoriteButton';
import ScrollTop from '@/components/common/ScrollTop';
import ToolEditButton from '@/components/tools/ToolEditButton';
import ToolImage from '@/components/tools/ToolImage';
import ToolInfoSection from '@/components/tools/ToolInfoSection';
import ToolMenu from '@/components/tools/ToolMenu';

export default {
	name: 'ToolInfo',
	components: {
		AuthorDetails,
		FavoriteButton,
		ToolEditButton,
		ToolInfoSection,
		ScrollTop,
		ToolImage,
		ToolMenu
	},
	props: {
		tool: {
			type: Object,
			default: null
		},
		revId: {
			type: [ String, Number ],
			default: null
		}
	},
	computed: {
		...mapState( 'locale', [ 'localeMap' ] ),
		attributesSection() {
			const items = [
				{
					title: this.$t( 'tooltype' ),
					param: 'tool_type__term',
					terms: [ this.buildTerm(
						'tool_type',
						this.getDisplayedScalar( 'tool_type' )
					) ].filter( ( e ) => e )
				},
				{
					title: this.$t( 'forwikis' ),
					param: 'wiki__term',
					terms: this.getDisplayedArray( 'for_wikis' ).map(
						_.partial( this.buildTerm, 'wiki' )
					)
				},
				{
					title: this.$t( 'audiences' ),
					param: 'audiences__term',
					terms: this.tool.annotations.audiences.map(
						_.partial( this.buildTerm, 'audiences' )
					)
				},
				{
					title: this.$t( 'contenttypes' ),
					param: 'content_types__term',
					terms: this.tool.annotations.content_types.map(
						_.partial( this.buildTerm, 'content_types' )
					)
				},
				{
					title: this.$t( 'tasks' ),
					param: 'tasks__term',
					terms: this.tool.annotations.tasks.map(
						_.partial( this.buildTerm, 'tasks' )
					)

				},
				{
					title: this.$t( 'subjectdomains' ),
					param: 'subject_domains__term',
					terms: this.tool.annotations.subject_domains.map(
						_.partial( this.buildTerm, 'subject_domains' )
					)
				},
				{
					title: this.$t( 'availableuilanguages' ),
					param: 'ui_language__term',
					terms: this.getDisplayedArray( 'available_ui_languages' ).map(
						_.partial( this.buildTerm, 'ui_language' )
					)
				},
				{
					title: this.$t( 'search-filter-keywords' ),
					param: 'keywords__term',
					terms: ( this.tool.keywords || [] ).filter(
						( e ) => e
					).map(
						_.partial( this.buildTerm, 'keyword' )
					)
				},
				{
					title: this.$t( 'search-filter-origin' ),
					param: 'origin__term',
					terms: [
						this.buildTerm( 'origin', this.tool.origin )
					].filter( ( e ) => e )
				}
			];
			return this.removeEmptyItems( items );
		},
		usageSection() {
			const items = [
				{
					title: this.$t( 'url' ),
					href: this.tool.url
				},
				{
					title: this.$t( 'urlalternates' ),
					href: this.tool.url_alternates
				},
				{
					title: this.$t( 'apidocumentation' ),
					href: this.getDisplayedScalar( 'api_url' )
				},
				{
					title: this.$t( 'howtouse' ),
					href: this.getDisplayedArray( 'user_docs_url' )
				},
				{
					title: this.$t( 'leavefeedback' ),
					href: this.getDisplayedArray( 'feedback_url' )
				},
				{
					title: this.$t( 'privacypolicy' ),
					href: this.getDisplayedArray( 'privacy_policy_url' )
				},
				{
					title: this.$t( 'bugtracker' ),
					href: this.getDisplayedScalar( 'bugtracker_url' )
				}
			];
			return this.removeEmptyItems( items );
		},
		contributingSection() {
			const items = [
				{
					title: this.$t( 'license' ),
					param: 'license__term',
					terms: [
						this.buildTerm( 'license', this.tool.license )
					].filter( ( e ) => e )
				},
				{
					title: this.$t( 'repository' ),
					href: this.tool.repository
				},
				{
					title: this.$t( 'developerdocumentation' ),
					href: this.getDisplayedArray( 'developer_docs_url' )
				},
				{
					title: this.$t( 'helptranslate' ),
					href: this.getDisplayedScalar( 'translate_url' )
				},
				{
					title: this.$t( 'technologyused' ),
					value: this.tool.technology_used
				}
			];
			return this.removeEmptyItems( items );
		},
		moreInfoSection() {
			const items = [
				{
					title: this.$t( 'sponsor' ),
					value: this.tool.sponsor
				},
				{
					title: this.$t( 'wikidataqid' ),
					value: this.tool.annotations.wikidata_qid,
					href: 'https://www.wikidata.org/wiki/' +
						encodeURIComponent( this.tool.annotations.wikidata_qid )
				},
				{
					title: this.$t( 'openhubid' ),
					value: this.tool.openhub_id,
					href: 'https://openhub.net/p/' +
						encodeURIComponent( this.tool.openhub_id )
				},
				{
					title: this.$t( 'botusername' ),
					value: this.tool.bot_username,
					href: 'https://meta.wikimedia.org/wiki/Special:CentralAuth/' +
						encodeURIComponent( this.tool.bot_username )
				}
			];
			return this.removeEmptyItems( items );
		}
	},
	methods: {
		/**
		 * Get the displayed value for an array typed toolinfo property.
		 *
		 * @param {string} field - toolinfo property name
		 * @return {Array} Core or annotation value for the given field name
		 */
		getDisplayedArray( field ) {
			const tool_val = ensureArray( this.tool[ field ] );
			const ann_val = ensureArray( this.tool.annotations[ field ] );
			return tool_val.length > 0 ? tool_val : ann_val;
		},
		/**
		 * Get the displayed value for a toolinfo property.
		 *
		 * @param {string} field - toolinfo property name
		 * @return {*} Core or annotation value for the given field name
		 */
		getDisplayedScalar( field ) {
			return this.tool[ field ] || this.tool.annotations[ field ];
		},
		/**
		 * Build a search term description object.
		 *
		 * @param {string} facet - facet name
		 * @param {string} value - facet value
		 * @return {Object}
		 */
		buildTerm( facet, value ) {
			if ( value === null ) {
				return null;
			}
			return {
				label: this.localizeLabel( facet, value ),
				term: value
			};
		},
		/**
		 * Get a localized label for a given facet value.
		 *
		 * @param {string} facet - facet name
		 * @param {string} value - facet value
		 * @return {string}
		 */
		localizeLabel( facet, value ) {
			switch ( facet ) {
				case 'ui_language':
					return this.$i18n.t(
						'search-filter-ui-language-value',
						[ this.localeMap[ value ] || value, value ]
					);
				case 'wiki':
					return forWikiLabel( value );
				case 'keyword':
				case 'license':
					return value;
				default:
					return localizeEnum( facet, value );
			}
		},
		/**
		 * Filter values considered "empty" from a list.
		 *
		 * @param {Array} items - list to filter
		 * @return {Array} list with empty values removed
		 */
		removeEmptyItems( items ) {
			return items.filter( function ( item ) {
				return (
					item.value &&
					item.value.length !== 0
				) || (
					item.value === undefined &&
					item.href &&
					item.href.length !== 0
				) || (
					item.terms &&
					item.terms.length !== 0
				);
			} );
		}
	}
};
</script>
