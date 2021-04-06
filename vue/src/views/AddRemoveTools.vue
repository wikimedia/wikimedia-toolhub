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
				<v-tabs
					v-model="tabs"
				>
					<v-tab>{{ $t( 'createnewtool' ) }}</v-tab>
					<v-tab>{{ $t( 'submitjsonurl' ) }}</v-tab>
				</v-tabs>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-tabs-items v-model="tabs">
					<v-tab-item>
						<CreateNewTool />
					</v-tab-item>

					<v-tab-item>
						<RegisterToolUrl />
					</v-tab-item>
				</v-tabs-items>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import CreateNewTool from '@/components/tools/CreateNewTool';
import RegisterToolUrl from '@/components/tools/RegisterToolUrl';

export default {
	components: {
		CreateNewTool,
		RegisterToolUrl
	},
	data() {
		return {
			tabs: null
		};
	}
};
</script>
