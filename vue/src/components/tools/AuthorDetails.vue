<template>
	<v-menu
		open-on-hover
		open-on-click
		:close-on-content-click="false"
		min-width="250px"
	>
		<template #activator="{ on, attrs }">
			<v-btn
				small
				rounded
				:ripple="false"
				v-bind="attrs"
				class="me-1 my-1"
				v-on="on"
			>
				{{ authorLayout.name.value }}
			</v-btn>
		</template>

		<v-card
			class="mx-auto"
			min-width="auto"
		>
			<v-card-text>
				<dl
					v-for="key in Object.keys( authorLayout )"
					:key="key"
					class="row ma-1"
				>
					<dt
						class="me-1 font-weight-bold"
					>
						<v-icon>
							{{ authorLayout[key].icon }}
						</v-icon>
						{{ authorLayout[key].label }}
					</dt>
					<dd class="line-clamp">
						<a
							v-if="isValidUrl( authorLayout[key].value )"
							:href="authorLayout[key].value"
							target="_blank"
						>
							{{ authorLayout[key].value }}
						</a>
						<template v-else>
							{{ authorLayout[key].value }}
						</template>
					</dd>
				</dl>
			</v-card-text>
			<v-card-actions>
				<v-btn
					block
					outlined
					color="primary"
					class="text-h6"
					:to="{
						name: 'search',
						query: { 'author__term': authorLayout.name.value }
					}"
				>
					<v-icon
						aria-hidden="false"
						:aria-label="$t( 'search' )"
					>
						mdi-magnify
					</v-icon>
					{{ $t( "author-menu-search-name" ) }}
				</v-btn>
			</v-card-actions>
		</v-card>
	</v-menu>
</template>

<script>
import { isValidHttpUrl } from '@/helpers/validation';

export default {
	name: 'AuthorDetails',
	props: {
		author: {
			type: Object,
			default: null
		}
	},
	computed: {
		authorLayout() {
			const layout = {
				name: {
					icon: 'mdi-account-outline',
					label: this.$t( 'name' ),
					value: this.author.name
				},
				wiki_username: {
					icon: 'mdi-card-account-details-outline',
					label: this.$t( 'wiki-username' ),
					value: this.author.wiki_username
				},
				developer_username: {
					icon: 'mdi-card-account-details-outline',
					label: this.$t( 'developer-username' ),
					value: this.author.developer_username
				},
				email: {
					icon: 'mdi-email-outline',
					label: this.$t( 'email' ),
					value: this.author.email
				},
				url: {
					icon: 'mdi-web',
					label: this.$t( 'url' ),
					value: this.author.url
				}
			};
			return Object.keys( layout ).reduce(
				( acc, key ) => {
					// remove fields that have no input
					if ( layout[ key ].value ) {
						acc[ key ] = layout[ key ];
					}
					return acc;
				},
				{}
			);
		}
	},
	methods: {
		isValidUrl( value ) {
			return isValidHttpUrl( value );
		}
	}
};
</script>
