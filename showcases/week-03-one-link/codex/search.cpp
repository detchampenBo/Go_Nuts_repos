// PROTOTYPE: exhaustive single-edge search on an undirected simple graph.
// Compile: clang++ -O3 -std=c++17 search.cpp -o /tmp/one-link-search
#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
using namespace std;
vector<double> centrality(const vector<vector<int>>& adj) {
  int n=adj.size(); vector<double> b(n), sigma(n), dep(n);
  vector<int> d(n), q(n);
  for(int s=0;s<n;s++) {
    fill(d.begin(),d.end(),-1); fill(sigma.begin(),sigma.end(),0);
    fill(dep.begin(),dep.end(),0); d[s]=0; sigma[s]=1;
    int head=0,tail=1;q[0]=s;
    while(head<tail) {
      int v=q[head++];
      for(int w:adj[v]) {
        if(d[w]<0){d[w]=d[v]+1;q[tail++]=w;}
        if(d[w]==d[v]+1)sigma[w]+=sigma[v];
      }
    }
    for(int k=tail-1;k>=0;k--) {
      int w=q[k];
      for(int v:adj[w])if(d[v]==d[w]-1)dep[v]+=sigma[v]/sigma[w]*(1+dep[w]);
      if(w!=s)b[w]+=dep[w];
    }
  }
  for(double &x:b)x/=double(n-1)*(n-2);
  return b;
}
int main(){
  int n,m;cin>>n>>m;vector<vector<int>> a(n);vector<vector<bool>> linked(n,vector<bool>(n));
  for(int k=0,u,v;k<m;k++){cin>>u>>v;a[u].push_back(v);a[v].push_back(u);linked[u][v]=linked[v][u]=true;}
  auto base=centrality(a); double best=-1;int bu=0,bv=0,bt=0,count=0;
  vector<double> after;
  for(int u=0;u<n;u++) {
    for(int v=u+1;v<n;v++)if(!linked[u][v]) {
      a[u].push_back(v);a[v].push_back(u);auto b=centrality(a);a[u].pop_back();a[v].pop_back();count++;
      for(int t=0;t<n;t++)if(base[t]-b[t]>best){best=base[t]-b[t];bu=u;bv=v;bt=t;after=b;}
    }
    if(u%25==0)cerr<<count<<" candidate links checked\n";
  }
  cout<<setprecision(15)<<"{\"u\":"<<bu<<",\"v\":"<<bv<<",\"broker\":"<<bt<<",\"drop\":"<<best<<",\"before\":"<<base[bt]<<",\"after\":"<<after[bt]<<",\"candidates\":"<<count<<"}\n";
}
