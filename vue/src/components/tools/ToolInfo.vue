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
			<v-btn
				v-if="$can( 'change', 'toolinfo/annotations' )"
				:to="{ name: 'tools-edit', params: { name: tool.name } }"
				color="primary base100--text my-1 mx-2"
				:small="$vuetify.breakpoint.smAndDown"
			>
				<v-icon class="me-2">
					mdi-pencil
				</v-icon>
				{{ $t( 'tools-edit' ) }}
			</v-btn>
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
			v-if="tool"
			class="mt-6"
			dense
		>
			<v-col md="7"
				cols="12"
				class="pe-4 mt-4"
			>
				<v-row>
					<v-col lg="2"
						md="3"
						sm="2"
						cols="12"
					>
						<ToolImage :tool="tool" />
					</v-col>
					<v-col lg="10"
						md="9"
						sm="10"
						cols="12"
					>
						<h2 class="text-h4">
							{{ tool.title }}
						</h2>

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

						<div
							v-if="tool.keywords"
							class="mt-4"
						>
							<v-chip
								v-for="tt in tool.keywords.filter( e => e )"
								:key="tt"
								:to="{ name: 'search', query: { 'keywords__term': tt } }"
								:ripple="false"
								class="ma-1 opacity-1"
							>
								{{ tt }}
							</v-chip>
						</div>

						<v-row class="mt-8">
							<v-btn
								class="ms-3"
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
								v-if="tool.repository || tool.annotations.repository"
								outlined
								color="primary base100--text"
								class="ms-3"
								:href="tool.repository || tool.annotations.repository"
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
						</v-row>

						<div
							v-if="links.length > 0"
							class="text-h5 mt-4"
						>
							{{ $t( 'links' ) }}
						</div>

						<v-list>
							<v-list-item
								v-for="link in links"
								:key="link.title"
								class="pa-0"
								dense
							>
								<v-list-item-content>
									<v-list-item-title
										v-if="link.url"
										class="mb-2"
									>
										{{ link.title }}
									</v-list-item-title>

									<template
										v-if="Array.isArray( link.url )"
									>
										<v-list-item
											v-for="( url, idx ) in link.url"
											:key="idx"
											class="pa-0 tool-links"
										>
											<v-list-item-subtitle>
												<a :href="url.url"
													target="_blank"
												>
													{{ url.url }}</a>
												<template
													v-if="url.language &&
														url.language !== $i18n.locale"
												>
													({{ url.language }})
												</template>
											</v-list-item-subtitle>
										</v-list-item>
									</template>
									<template
										v-else
									>
										<v-list-item-subtitle>
											<a :href="link.url"
												target="_blank"
											>
												{{ link.url }}
											</a>
										</v-list-item-subtitle>
									</template>
								</v-list-item-content>
							</v-list-item>
						</v-list>
					</v-col>
				</v-row>
			</v-col>
			<v-col md="5" cols="12">
				<v-divider
					v-if="$vuetify.breakpoint.smAndDown"
					class="mt-4"
				/>

				<div
					v-if="moreInfoItems && moreInfoItems.length > 0"
					class="text-h5 mt-4"
				>
					{{ $t( 'moreinfo' ) }}
				</div>
				<v-card
					class="mt-4"
				>
					<v-simple-table
						light
					>
						<template #default>
							<tbody>
								<tr
									v-for="item in moreInfoItems"
									:key="item.name"
								>
									<td>{{ item.name }}</td>
									<td
										v-if="Array.isArray( item.value )"
									>
										<v-chip
											v-for="iv in item.value"
											:key="iv"
											:ripple="false"
											disabled
											class="ma-1 opacity-1"
										>
											{{ iv }}
										</v-chip>
									</td>
									<td
										v-else
									>
										{{ item.value }}
									</td>
								</tr>
							</tbody>
						</template>
					</v-simple-table>
				</v-card>

				<v-alert
					v-if="( tool.experimental || tool.deprecated ||
						tool.annotations.experimental || tool.annotations.deprecated )"
					border="left"
					type="error"
					elevation="2"
					width="100%"
					class="mt-4"
				>
					<template v-if="tool.experimental || tool.annotations.experimental">
						{{ $t( 'tool-experimental-error' ) }}
					</template>

					<template v-if="tool.deprecated || tool.annotations.deprecated">
						{{ $t( 'tool-deprecated-error' ) }}
					</template>
				</v-alert>

				<v-alert
					v-if="tool.replaced_by || tool.annotations.replaced_by"
					border="left"
					color="primary base100--text"
					dark
					elevation="2"
					type="info"
					width="100%"
					class="mt-4"
				>
					{{ $t( 'tool-replacement-link',
						[ tool.replaced_by || tool.annotations.replaced_by ] ) }}
				</v-alert>
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
import _ from 'lodash';

import { ensureArray } from '@/helpers/array';
import { forWikiLabel, localizeEnum } from '@/helpers/tools';

import AuthorDetails from '@/components/tools/AuthorDetails';
import FavoriteButton from '@/components/tools/FavoriteButton';
import ScrollTop from '@/components/common/ScrollTop';
import ToolImage from '@/components/tools/ToolImage';
import ToolMenu from '@/components/tools/ToolMenu';

export default {
	name: 'ToolInfo',
	components: {
		AuthorDetails,
		FavoriteButton,
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
		links() {
			const links = [
				{
					title: this.$t( 'apidocumentation' ),
					url: this.tool.api_url || this.tool.annotations.api_url
				},
				{
					title: this.$t( 'helptranslate' ),
					url: this.tool.translate_url || this.tool.annotations.translate_url
				},
				{
					title: this.$t( 'bugtracker' ),
					url: this.tool.bugtracker_url || this.tool.annotations.bugtracker_url
				},
				{
					title: this.$t( 'howtouse' ),
					url: this.getArray( this.tool, 'user_docs_url' )
				},
				{
					title: this.$t( 'developerdocumentation' ),
					url: this.getArray( this.tool, 'developer_docs_url' )
				},
				{
					title: this.$t( 'leavefeedback' ),
					url: this.getArray( this.tool, 'feedback_url' )
				},
				{
					title: this.$t( 'privacypolicy' ),
					url: this.getArray( this.tool, 'privacy_policy_url' )
				},
				{
					title: this.$t( 'urlalternates' ),
					url: this.tool.url_alternates
				}
			];

			// Remove empty links from the list
			const filteredLinks = links.filter( function ( link ) {
				return link.url && link.url.length !== 0;
			} );

			return filteredLinks;
		},
		moreInfoItems() {
			const items = [
				{
					name: this.$t( 'tooltype' ),
					value: localizeEnum(
						'tool_type',
						this.tool.tool_type || this.tool.annotations.tool_type
					)
				},
				{
					name: this.$t( 'forwikis' ),
					value: this.getArray( this.tool, 'for_wikis' ).map( forWikiLabel )
				},
				{
					name: this.$t( 'audiences' ),
					value: this.tool.annotations.audiences.map(
						_.partial( localizeEnum, 'audiences' )
					)
				},
				{
					name: this.$t( 'contenttypes' ),
					value: this.tool.annotations.content_types.map(
						_.partial( localizeEnum, 'content_types' )
					)
				},
				{
					name: this.$t( 'tasks' ),
					value: this.tool.annotations.tasks.map(
						_.partial( localizeEnum, 'tasks' )
					)

				},
				{
					name: this.$t( 'subjectdomains' ),
					value: this.tool.annotations.subject_domains.map(
						_.partial( localizeEnum, 'subject_domains' )
					)
				},
				{
					name: this.$t( 'availableuilanguages' ),
					value: this.getArray( this.tool, 'available_ui_languages' )
				},
				{
					name: this.$t( 'license' ),
					value: this.tool.license
				},
				{
					name: this.$t( 'sponsor' ),
					value: this.tool.sponsor
				},
				{
					name: this.$t( 'technologyused' ),
					value: this.tool.technology_used
				},
				{
					name: this.$t( 'wikidataqid' ),
					value: this.tool.annotations.wikidata_qid
				}
			];

			const filteredItems = items.filter( ( item ) => {
				return item.value &&
					item.value !== null &&
					item.value.length !== 0;
			} );

			return filteredItems;
		}
	},
	methods: {
		getArray( tool, key ) {
			const tool_array = ensureArray( tool[ key ] );
			const annotations_array = ensureArray( tool.annotations[ key ] );

			const array = tool_array.length > 0 ? tool_array : annotations_array;

			return array;
		}
	}
};
</script>
