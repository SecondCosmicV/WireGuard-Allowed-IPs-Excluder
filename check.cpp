#include <string>
#include <vector>
#include <stack>
#include <sstream>
#include <iostream>
#include <fstream>
#include <cassert>
using namespace std;
typedef struct {
    string ip_str;
    unsigned first_ip,last_ip;
}IPRange;
void parse_ip_range(IPRange *ip_range){
    int slash_idx=ip_range->ip_str.find('/');
    string ip_str=ip_range->ip_str.substr(0,slash_idx);
    string subnet_mask_str=ip_range->ip_str.substr(slash_idx+1);
    stringstream ss(ip_str);
    int subnet_mask=stoi(subnet_mask_str);
    ip_range->first_ip=0;
    string octet;
    while(getline(ss,octet,'.'))
        ip_range->first_ip=(ip_range->first_ip<<8)|stoi(octet);
    ip_range->last_ip=ip_range->first_ip;
    for(int i=31-subnet_mask;~i;i--){
        ip_range->first_ip&=~(1<<i);
        ip_range->last_ip|=(1<<i);
    }
}
bool is_in_allowed_ips(unsigned ip,const vector<IPRange> &allowed_ips){
    for(const auto &x:allowed_ips){
        if(x.first_ip<=ip&&ip<=x.last_ip)
            return true;
    }
    return false;
}
int main(void){
    string token;
    cin>>token;
    assert(token=="AllowedIPs");
    cin>>token;
    assert(token=="=");
    vector<IPRange>allowed_ips;
    while(cin>>token){
        if(token.back()==',')
            token.pop_back();
        IPRange ip_range;
        ip_range.ip_str=token;
        parse_ip_range(&ip_range);
        allowed_ips.push_back(ip_range); 
    }
    ifstream test_file_stream("subnet_masks/test.txt");
    string line;
    vector<pair<bool,IPRange>>test_file;
    while(getline(test_file_stream,line)){
        if(line.empty()||line[0]=='#')
            continue;
        stringstream ss(line);
        ss>>token;
        bool is_in;
        if(token=="IN:")
            is_in=true;
        else if(token=="EX:")
            is_in=false;
        else
            assert(false);
        IPRange ip_range;
        ss>>ip_range.ip_str;
        parse_ip_range(&ip_range);
        test_file.push_back({is_in,ip_range});
    }
    unsigned ip=0U;
    while(true){
        if(!(ip%1000000)||ip==~0U)
            cout<<"Verifying AllowedIPs... "<<((((long long)ip)*100)/~0U)<<"%\r"<<flush;
        bool expect;
        bool hit=false;
        for(int i=test_file.size()-1;~i;i--){
            if(test_file[i].second.first_ip<=ip&&ip<=test_file[i].second.last_ip){
                expect=test_file[i].first;
                hit=true;
                break;
            }
        }
        assert(hit);
        if(is_in_allowed_ips(ip,allowed_ips)!=expect){
            stack<unsigned>st;
            for(int i=0;i<4;i++){
                st.push(ip%256);
                ip>>=8;
            }
            cout<<endl<<"FAIL: ";
            while(true){
                cout<<st.top();
                st.pop();
                if(st.empty())
                    break;
                else
                    cout<<'.';
            }
            cout<<"/32";
            cout<<" should be "<<(expect?"allowed":"disallowed");
            cout<<", but it is "<<(expect?"disallowed":"allowed")<<'.'<<endl;
            return 1;
        }
        if(ip==~0U)
            break;
        ip++;
    }
    cout<<endl<<"OK"<<endl;
    return 0;
}

