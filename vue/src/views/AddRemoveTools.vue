<template>
	<v-container>
		<v-row>
			<v-col
				cols="12"
			>
				<h2 class="text-h4">
					{{ $t( 'addremovetools' ) }}
				</h2>
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
import CreateNewTool from '@/components/tools/CreateNewTool';
import RegisterToolUrl from '@/components/tools/RegisterToolUrl';
import fetchMetaInfo from '@/helpers/metadata';

export default {
	components: {
		CreateNewTool,
		RegisterToolUrl
	},
	data() {
		return {
			items: [
				{
					href: 'tool-create',
					label: this.$t( 'createnewtool' ),
					component: 'CreateNewTool'
				},
				{
					href: 'urls',
					label: this.$t( 'submitjsonurl' ),
					component: 'RegisterToolUrl'
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
		return fetchMetaInfo( 'addremovetools' );
	},
	mounted() {
		this.$store.dispatch( 'user/getUserInfo', { vm: this } ).then(
			( user ) => {
				if ( !user.is_authenticated ) {
					this.$notify.info(
						this.$t( 'addremovetools-nologintext' )
					);
				}
			}
		);
	}
};
</script>
