<template>
	<v-container>
		<v-row dense>
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
						<v-icon
							v-if="!toolInfo.icon"
							size="100"
						>
							mdi-tools
						</v-icon>

						<v-img
							v-if="toolInfo.icon"
							:src="toolInfo.icon.img"
							max-height="100"
							max-width="100"
						/>
					</v-col>
					<v-col lg="10"
						md="9"
						sm="10"
						cols="12"
					>
						<h2 class="display-1">
							{{ toolInfo.title }}
						</h2>

						<div class="mt-4" dir="auto">
							{{ toolInfo.description }}
						</div>

						<dl class="row mx-0 mt-4 subtitle-2">
							<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
							<dd>{{ toolInfo.author }}</dd>
						</dl>

						<v-chip-group
							v-if="toolInfo.keywords"
							active-class="primary--text"
							class="mt-4"
							column
						>
							<v-chip
								v-for="tt in toolInfo.keywords.filter(e => e)"
								:key="tt"
							>
								{{ tt }}
							</v-chip>
						</v-chip-group>

						<v-row>
							<v-btn
								v-if="toolInfo.repository"
								class="mt-4 ms-3"
								color="primary"
								dark
								:href="`${toolInfo.repository}`"
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
								:href="`${toolInfo.url}`"
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
					v-if="toolInfo.experimental"
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
					v-if="toolInfo.deprecated"
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
import { mapState } from 'vuex';
import i18n from '@/plugins/i18n';

export default {
	name: 'Tool',
	data() {
		return {
			toolName: this.$route.params.name
		};
	},
	computed: {
		...mapState( 'tools', [ 'toolInfo' ] ),
		links() {
			const links = [
				{
					title: this.$t( 'howtouse' ),
					url: this.toolInfo.user_docs_url
				},
				{
					title: this.$t( 'developerdocumentation' ),
					url: this.toolInfo.developer_docs_url
				},
				{
					title: this.$t( 'apidocumentation' ),
					url: this.toolInfo.api_url
				},
				{
					title: this.$t( 'helptranslate' ),
					url: this.toolInfo.translate_url
				},
				{
					title: this.$t( 'privacypolicy' ),
					url: this.toolInfo.privacy_policy_url
				},
				{
					title: this.$t( 'leavefeedback' ),
					url: this.toolInfo.feedback_url
				},
				{
					title: this.$t( 'bugtracker' ),
					url: this.toolInfo.bugtracker_url
				}
			];

			const filteredLinks = links.filter( function ( link ) {
				return link.url && link.url.length !== 0;
			} );

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
				}
				return link;
			} );

			return localizedLinks;
		},
		moreInfoItems() {
			const items = [
				{
					name: this.$t( 'tooltype' ),
					value: this.toolInfo.tool_type
				},
				{
					name: this.$t( 'forwikis' ),
					value: this.toolInfo.for_wikis
				},
				{
					name: this.$t( 'technologyused' ),
					value: this.toolInfo.technology_used
				}
			];

			const filteredItems = items.filter( function ( item ) {
				return ( item.value && item.value.length !== 0 ) && item.value !== null;
			} );

			return filteredItems;
		}
	},
	methods: {
		getToolInfo() {
			this.$store.dispatch( 'tools/getToolInfo', this.toolName );
		}
	},
	mounted() {
		this.getToolInfo();
	}
};
</script>
