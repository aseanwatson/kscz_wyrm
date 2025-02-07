module udp_panel_writer
    #(parameter PORT_MSB = 8'h80)
    (input  wire          clk,
    input  wire          reset,
    input  wire          udp_source_valid,
    input  wire          udp_source_last,
    output reg           udp_source_ready,
    input  wire  [15:0]  udp_source_src_port,
    input  wire  [15:0]  udp_source_dst_port,
    input  wire  [31:0]  udp_source_ip_address,
    input  wire  [15:0]  udp_source_length,
    input  wire  [31:0]  udp_source_data,
    input  wire  [3:0]   udp_source_error,
    
    output reg [5:0]     ctrl_en,
    output reg [15:0]    ctrl_addr,
    output reg [23:0]    ctrl_wdat,
    
    output reg led_reg
);

reg [31:0] src_ip;
reg [1:0] byte_count;
initial udp_source_ready <= 1'b0;

always @(posedge clk) begin
    if (reset) begin
        udp_source_ready <= 1'b0;
        led_reg   <= 1'b1;
        ctrl_addr <= 16'b0;
        ctrl_wdat <= 24'b0;
        ctrl_en   <= 6'b0;
    end else begin
        if (udp_source_valid & (udp_source_dst_port[15:8] == PORT_MSB)) begin
            ctrl_en          <= udp_source_dst_port[5:0];
            ctrl_addr        <= udp_source_data[31:18];
            ctrl_wdat[23:16] <= udp_source_data[17:12];
            ctrl_wdat[15:8]  <= udp_source_data[11:6];
            ctrl_wdat[7:0]   <= udp_source_data[5:0];
        end else begin
            ctrl_en <= 6'b0;
        end
    end
end

endmodule
