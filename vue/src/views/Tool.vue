<template>
	<v-container>
		<v-row
			v-if="tool"
			dense
		>
			<v-col md="7"
				cols="12"
				class="me-8"
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
						<h2 class="display-1">
							{{ tool.title }}
						</h2>

						<div class="mt-4" dir="auto">
							{{ tool.description }}
						</div>

						<dl class="row mx-0 mt-4 subtitle-2">
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
							class="headline mt-4"
						>
							{{ $t( 'links' ) }}
						</div>

						<v-list>
							<v-list-item
								v-for="link in links"
								:key="link.title"
								class="pa-0"
							>
								<a
									:href="`${link.url}`"
									target="_blank"
								>
									{{ link.title }}
								</a>
							</v-list-item>
						</v-list>
					</v-col>
				</v-row>
			</v-col>
			<v-col md="4" cols="12">
				<v-divider
					v-if="$vuetify.breakpoint.smAndDown"
				/>

				<div
					v-if="moreInfoItems && moreInfoItems.length > 0"
					class="headline mt-4"
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
					v-if="tool.experimental"
					border="left"
					color="primary"
					dark
					elevation="2"
					type="info"
					width="100%"
					class="mt-4"
				>
					{{ $t( 'tool-experimental-error' ) }}
				</v-alert>

				<v-alert
					v-if="tool.deprecated"
					border="left"
					type="error"
					elevation="2"
					width="100%"
				>
					{{ $t( 'tool-deprecated-error' ) }}
				</v-alert>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';
import i18n from '@/plugins/i18n';
import CommonsImage from '@/components/tools/CommonsImage';

export default {
	name: 'Tool',
	components: {
		CommonsImage
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
					title: this.$t( 'howtouse' ),
					url: this.tool.user_docs_url
				},
				{
					title: this.$t( 'developerdocumentation' ),
					url: this.tool.developer_docs_url
				},
				{
					title: this.$t( 'apidocumentation' ),
					url: this.tool.api_url
				},
				{
					title: this.$t( 'helptranslate' ),
					url: this.tool.translate_url
				},
				{
					title: this.$t( 'privacypolicy' ),
					url: this.tool.privacy_policy_url
				},
				{
					title: this.$t( 'leavefeedback' ),
					url: this.tool.feedback_url
				},
				{
					title: this.$t( 'bugtracker' ),
					url: this.tool.bugtracker_url
				}
			];

			// Remove empty links from the list
			const filteredLinks = links.filter( function ( link ) {
				return link.url && link.url.length !== 0;
			} );

			// Select "best" langauge match link for localized collections
			const localizedLinks = filteredLinks.map( ( link ) => {
				if ( Array.isArray( link.url ) ) {
					const urls = link.url.reduce( ( out, value ) => {
						return {
							...out,
							[ value.language ]: value.url
						};
					}, {} );
					// eslint-disable-next-line no-underscore-dangle
					const fallbackChain = i18n._getLocaleChain(
						i18n.locale, i18n.fallbackLocale
					);
					for ( const value of fallbackChain ) {
						if ( urls[ value ] ) {
							link.url = urls[ value ];
							break;
						}
					}
					if ( Array.isArray( link.url ) ) {
						// T277260: No locale in the fallback chain was found.
						// Pick the first link in the list as the default.
						link.url = link.url[ 0 ].url;
					}
				}
				return link;
			} );

			return localizedLinks;
		},
		moreInfoItems() {
			const items = [
				{
					name: this.$t( 'tooltype' ),
					value: this.tool.tool_type
				},
				{
					name: this.$t( 'forwikis' ),
					value: this.tool.for_wikis
				},
				{
					name: this.$t( 'technologyused' ),
					value: this.tool.technology_used
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
