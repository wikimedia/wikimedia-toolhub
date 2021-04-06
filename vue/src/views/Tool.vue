<template>
	<v-container>
		<v-app-bar
			v-if="tool"
			color="bgtext"
			dense
			flat
		>
			<v-spacer />
			<v-btn
				v-if="canEdit"
				:to="`/tool/${tool.name}/edit`"
				color="primary"
			>
				<v-icon class="me-2">
					mdi-pencil
				</v-icon>
				{{ $t( 'edittool' ) }}
			</v-btn>
		</v-app-bar>

		<v-row
			v-if="tool"
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
						<CommonsImage :commons-url="tool.icon" />
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

						<dl class="row mx-0 mt-4 text-subtitle-1">
							<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
							<dd>{{ tool.author }}</dd>
						</dl>

						<v-chip-group
							v-if="tool.keywords"
							active-class="primary--text"
							class="mt-4"
							column
						>
							<v-chip
								v-for="tt in tool.keywords.filter(e => e)"
								:key="tt"
							>
								{{ tt }}
							</v-chip>
						</v-chip-group>

						<v-row>
							<v-btn
								v-if="tool.repository"
								class="mt-4 ms-3"
								color="primary"
								dark
								:href="`${tool.repository}`"
								target="_blank"
							>
								{{ $t( 'sourcecode' ) }}
								<v-icon
									dark
									right
								>
									mdi-code-json
								</v-icon>
							</v-btn>

							<v-btn
								class="mt-4 ms-3"
								color="primary"
								dark
								:href="`${tool.url}`"
								target="_blank"
							>
								{{ $t( 'browsetool' ) }}
								<v-icon
									dark
									right
								>
									mdi-link-variant
								</v-icon>
							</v-btn>
						</v-row>

						<v-divider class="mt-8" />

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
										v-if="Array.isArray(link.url)"
									>
										<v-list-item
											v-for="(url, idx) in link.url"
											:key="idx"
											class="pa-0 tool-links"
										>
											<v-list-item-subtitle>
												<a :href="url.url"
													target="_blank"
												>
													{{ url.url }}</a>
												<template
													v-if="url.language && url.language
														!== $i18n.locale"
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
									<td>
										<v-chip-group
											v-if="Array.isArray(item.value)"
											column
										>
											<v-chip
												v-for="iv in item.value"
												:key="iv"
											>
												{{ iv }}
											</v-chip>
										</v-chip-group>
										<div
											v-else
										>
											{{ item.value }}
										</div>
									</td>
								</tr>
							</tbody>
						</template>
					</v-simple-table>
				</v-card>

				<v-alert
					v-if="tool.experimental || tool.deprecated"
					border="left"
					type="error"
					elevation="2"
					width="100%"
					class="mt-4"
				>
					<template v-if="tool.experimental">
						{{ $t( 'tool-experimental-error' ) }}
					</template>

					<template v-if="tool.deprecated">
						{{ $t( 'tool-deprecated-error' ) }}
					</template>
				</v-alert>

				<v-alert
					v-if="tool.replaced_by"
					border="left"
					color="primary"
					dark
					elevation="2"
					type="info"
					width="100%"
					class="mt-4"
				>
					{{ $t( 'tool-replacement-link', [ tool.replaced_by ] ) }}
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
import { mapActions, mapMutations, mapState } from 'vuex';
import { ensureArray } from '@/helpers/array';
import { forWikiLabel } from '@/helpers/tools';
import CommonsImage from '@/components/tools/CommonsImage';
import ScrollTop from '@/components/tools/ScrollTop';

export default {
	name: 'Tool',
	components: {
		CommonsImage,
		ScrollTop
	},
	data() {
		return {
			name: this.$route.params.name
		};
	},
	computed: {
		...mapState( 'tools', [ 'tool' ] ),
		links() {
			const links = [
				{
					title: this.$t( 'apidocumentation' ),
					url: this.tool.api_url
				},
				{
					title: this.$t( 'helptranslate' ),
					url: this.tool.translate_url
				},
				{
					title: this.$t( 'bugtracker' ),
					url: this.tool.bugtracker_url
				},
				{
					title: this.$t( 'howtouse' ),
					url: this.tool.user_docs_url
				},
				{
					title: this.$t( 'developerdocumentation' ),
					url: this.tool.developer_docs_url
				},
				{
					title: this.$t( 'leavefeedback' ),
					url: this.tool.feedback_url
				},
				{
					title: this.$t( 'privacypolicy' ),
					url: this.tool.privacy_policy_url
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
					value: this.tool.tool_type
				},
				{
					name: this.$t( 'license' ),
					value: this.tool.license
				},
				{
					name: this.$t( 'availableuilanguages' ),
					value: this.tool.available_ui_languages
				},
				{
					name: this.$t( 'technologyused' ),
					value: this.tool.technology_used
				},
				{
					name: this.$t( 'sponsor' ),
					value: this.tool.sponsor
				},
				{
					name: this.$t( 'forwikis' ),
					value: ensureArray(
						this.tool.for_wikis ).map( forWikiLabel )
				}
			];

			const filteredItems = items.filter( ( item ) => {
				return item.value &&
					item.value !== null &&
					item.value.length !== 0;
			} );

			return filteredItems;
		},
		canEdit() {
			const username = this.$store.state.user.user.username;
			return this.tool.created_by.username === username &&
				this.tool.origin === 'api';
		}
	},
	methods: {
		...mapActions( 'tools', [ 'getToolByName' ] ),
		...mapMutations( 'tools', [ 'TOOL' ] )
	},
	mounted() {
		// Clear any data from a prior view
		this.TOOL( null );
		this.getToolByName( this.name );
	}
};
</script>
