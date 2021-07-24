<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'developersettings' ) }}
				</h2>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'developersettings-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<v-tabs v-model="tab">
					<v-tab
						v-for="item in items"
						:key="item.label"
						:href="'#' + item.href"
					>
						{{ item.label }}
					</v-tab>
				</v-tabs>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<v-tabs-items v-model="tab">
					<v-tab-item
						v-for="item in items"
						:key="item.label"
						:value="item.href"
					>
						<component :is="item.component" />
					</v-tab-item>
				</v-tabs-items>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import fetchMetaInfo from '@/helpers/metadata';
import RegisterApp from '@/components/oauth/RegisterApp';
import ClientApps from '@/components/oauth/ClientApps';
import AuthorizedApps from '@/components/oauth/AuthorizedApps';

export default {
	components: {
		RegisterApp,
		ClientApps,
		AuthorizedApps
	},
	data() {
		return {
			items: [
				{
					href: 'oauth-register',
					label: this.$t( 'registerapps' ),
					component: 'RegisterApp'
				},
				{
					href: 'oauth-clients',
					label: this.$t( 'clientapps' ),
					component: 'ClientApps'
				},
				{
					href: 'oauth-authorized',
					label: this.$t( 'authorizedapps' ),
					component: 'AuthorizedApps'
				}
			]
		};
	},
	computed: {
		tab: {
			set( tab ) {
				this.$router.replace( {
					query: { ...this.$route.query, tab }
				} );
			},
			get() {
				return this.$route.query.tab;
			}
		}
	},
	metaInfo() {
		return fetchMetaInfo( 'developersettings' );
	}
};
</script>
